from dotenv import load_dotenv
load_dotenv()

import os
import requests
import time
from datetime import datetime

WECOM_WEBHOOK_URL = os.getenv("WECOM_WEBHOOK_URL")
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL")

# 天气警报类型（根据天文台文档）
WARNING_TYPES = {
    'WFIRE': '火灾危险警告',
    'WFROST': '霜冻警告', 
    'WHOT': '酷热天气警告',
    'WCOLD': '寒冷天气警告',
    'WMSGNL': '强烈季候风信号',
    'WRAIN': '暴雨警告信号',
    'WFNTSA': '新界北部水浸特别报告',
    'WL': '山泥倾泻警告',
    'WTCSGNL': '热带气旋警告信号',
    'WTMW': '海啸警告',
    'WTS': '雷暴警告'
}

def get_hko_forecast():
    url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=tc"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # 打印所有日期，看哪个是明天
        for i, day in enumerate(data['weatherForecast'][:3]):
            print(f"Index {i}: {day.get('forecastDate')} ({day.get('week')})")
        
        # 明天 = 今天之后的第一天
        today_str = datetime.now().strftime("%Y%m%d")
        tomorrow = None
        
        for day in data['weatherForecast']:
            if day.get('forecastDate') > today_str:
                tomorrow = day
                break
        
        if not tomorrow:
            print("找不到明天的数据")
            return None
            
        return {
            'date': tomorrow.get('forecastDate'),
            'week': tomorrow.get('week'),
            'weather': tomorrow.get('forecastWeather'),
            'temp_high': tomorrow.get('forecastMaxtemp', {}).get('value'),
            'temp_low': tomorrow.get('forecastMintemp', {}).get('value'),
            'rain_chance': tomorrow.get('PSR', '低')
        }
    except Exception as e:
        print(f"获取天气失败：{e}")
        return None
        

# 只监控这些警报（即时推送）
URGENT_WARNINGS = {
    'WTS': '雷暴警告',
    'WRAIN': '暴雨警告信号',
    'WCOLD': '寒冷天气警告',
    'WFROST': '霜冻警告',
    'WTCSGNL': '热带气旋警告信号',
    'WMSGNL': '强烈季候风信号',
    'WHOT': '酷热天气警告',
    'WTMW': '海啸警告'
}

def check_weather_warnings():
    """检查特定天气警告（即时推送）"""
    url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warnsum&lang=tc"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        active_urgent = []
        for code, warning in data.items():
            if code in URGENT_WARNINGS and warning.get('actionCode') == 'ISSUE':
                active_urgent.append({
                    'code': code,
                    'name': URGENT_WARNINGS[code],
                    'type': warning.get('type', ''),
                    'issueTime': warning.get('issueTime', '')
                })
        
        if not active_urgent:
            print(f"[{datetime.now().strftime('%H:%M')}] 无关注的天气警告")
            return
        
        for warning in active_urgent:
            issue_time = warning.get('issueTime', '')
            if issue_time:
                try:
                    issue_dt = datetime.fromisoformat(issue_time.replace('Z', '+08:00'))
                    hours_since = (datetime.now() - issue_dt.replace(tzinfo=None)).total_seconds() / 3600
                    
                    if hours_since <= 1:
                        msg = f"""⚠️ {warning['name']}

类型：{warning.get('type', 'N/A')}
时间：{issue_time}

请注意安全！"""
                        
                        send_both(msg)
                        print(f"已推送：{warning['name']}")
                except:
                    pass
                    
    except Exception as e:
        print(f"检查警告失败：{e}")
def should_remind_weather(weather):
    """高/中高降雨概率 或 温差>8度时提醒"""
    rain_level = weather['rain_chance']
    need_rain_gear = rain_level in ['高', '中高']
    
    temp_diff = int(weather['temp_high']) - int(weather['temp_low'])
    return need_rain_gear or temp_diff >= 8

def send_wecom(message):
    data = {"msgtype": "text", "text": {"content": message}}
    requests.post(WECOM_WEBHOOK_URL, json=data)

def send_feishu(message):
    if "提醒" not in message and "警告" not in message:
        message = "提醒：" + message
    data = {"msg_type": "text", "content": {"text": message}}
    requests.post(FEISHU_WEBHOOK_URL, json=data)

def send_both(message):
    send_wecom(message)
    send_feishu(message)

def check_weather_forecast():
    """检查明日天气预报（每天推送）"""
    weather = get_hko_forecast()
    if not weather:
        return
    
    print(f"[{datetime.now().strftime('%H:%M')}] 明天（{weather['week']}）：{weather['weather']}")
    print(f"温度：{weather['temp_low']}-{weather['temp_high']}°C，降雨：{weather['rain_chance']}")
    
    msg = f"""🌤️ 明日天气（{weather['week']}）

天气：{weather['weather']}
温度：{weather['temp_low']}°C ~ {weather['temp_high']}°C
降雨概率：{weather['rain_chance']}"""
    
    send_both(msg)
    print("已推送")
def check_weather_warnings():
    """检查天气警告（即时推送）"""
    warnings = get_hko_warnings()
    
    if not warnings:
        print(f"[{datetime.now().strftime('%H:%M')}] 当前无天气警告")
        return
    
    # 检查是否有新警告（通过时间判断，简单版）
    for warning in warnings:
        # 只推送最近1小时内发布的警告
        issue_time = warning.get('issueTime', '')
        if issue_time:
            try:
                issue_dt = datetime.fromisoformat(issue_time.replace('Z', '+08:00'))
                hours_since_issue = (datetime.now() - issue_dt.replace(tzinfo=None)).total_seconds() / 3600
                
                if hours_since_issue <= 1:  # 1小时内新发布的
                    msg = f"""⚠️ 天气警告

{warning['name']}
类型：{warning.get('type', 'N/A')}
发布时间：{issue_time}

请注意安全！"""
                    
                    send_both(msg)
                    print(f"已推送警告：{warning['name']}")
            except Exception as e:
                print(f"解析时间失败：{e}")

def main():
    # 模式1：定时任务（GitHub Actions 21:00运行）- 只查天气预报
    # check_weather_forecast()
    
    # 模式2：持续监控（需要服务器或电脑一直开着）- 查天气警告
    print("开始监控天气警告（每10分钟检查一次）...")
    print("按 Ctrl+C 停止")
    
    try:
        while True:
            check_weather_warnings()
            time.sleep(600)  # 600秒 = 10分钟
    except KeyboardInterrupt:
        print("\n已停止监控")

if __name__ == "__main__":
    check_weather_forecast()