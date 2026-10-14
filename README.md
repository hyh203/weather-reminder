# Development Notes/声明

This is a personal learning project developed with substantial assistance from AI coding tools. I initiated the project, defined its intended functionality, and used AI-assisted workflows to implement and test the initial version. I am continuing to learn the underlying code and implementation details. The current version has passed the tests I have run, but this does not necessarily mean that all functionality is bug-free or production-ready.

请留意，此项目为个人学习作品，在开发过程中使用了大量人工智能协助。我本人定义其预期能达到的效果，并使用人工智能辅助我进行上述测试，我仍在学习相关底层代码与逻辑。此版本为测试版，取得了我认为满意的效果，但仍未达到完美状态，敬请留意。

---

# Weather Reminder HK

香港天气自动推送，支持企业微信和飞书双通道。

## 效果

- 每天 **北京时间 21:00** 自动推送明天天气预报
- 支持天气警报即时推送（雷暴、暴雨、寒冷、酷热等）
- 使用香港天文台官方数据，无需注册 API
- 双通道保障：企业微信 + 飞书同时推送

## 快速开始（Fork 使用）

### 第一步：Fork 这个仓库

点击右上角 **Fork**，复制到你的 GitHub 账号。

### 第二步：配置机器人（二选一或都配）

#### 企业微信
1. 下载企业微信 APP，创建群聊（只有自己也可以）
2. 群设置 → 群机器人 → 添加 → 复制 Webhook 地址

#### 飞书
1. 下载飞书 APP，创建群聊
2. 群设置 → 群机器人 → 添加机器人 → 自定义机器人
3. **安全设置**：添加关键词"天气"或"提醒"（必须，否则收不到消息）
4. 复制 Webhook 地址

### 第三步：添加到 GitHub Secrets

在你的 Fork 仓库中：
**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

添加两个 Secrets：

| Name | Value |
|------|-------|
| `WECOM_WEBHOOK_URL` | 你的企微 Webhook 地址 |
| `FEISHU_WEBHOOK_URL` | 你的飞书 Webhook 地址 |

### 第四步：测试

**Actions** → **Weather Reminder** → **Run workflow** 手动触发测试。

明天开始每天 21:00 自动推送。

## 本地运行（可选）

```bash
# 克隆项目
git clone https://github.com/hyh203/weather-reminder
cd weather-reminder

# 安装依赖
pip install requests python-dotenv

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的配置

# 运行（每天天气推送）
python weather.py

# 运行（天气警报监控，需一直开着）
python -c "from weather import check_weather_warnings; check_weather_warnings()"
```

## 功能说明

### 每日天气推送
- **数据源**：香港天文台开放数据 API
- **内容**：天气状况、温度范围、降雨概率
- **时间**：每天 21:00（北京时间）
- **基准**：自动获取明天（而非今天）的数据

### 天气警报即时推送
监控以下警报（发布时即时推送）：

| 警报类型 | 说明 |
|----------|------|
| ⚡ 雷暴警告 | 强对流天气 |
| 🌧️ 暴雨警告信号 | 黄/红/黑暴雨 |
| ❄️ 寒冷天气警告 | 低温预警 |
| 🔥 酷热天气警告 | 高温预警 |
| 🌀 热带气旋警告信号 | 台风/热带风暴 |
| 💨 强烈季候风信号 | 大风预警 |
| 🌊 海啸警告 | 海啸风险 |
| 🧊 霜冻警告 | 结霜风险 |

**注意**：即时推送需要电脑或服务器持续运行，GitHub Actions 免费版有延迟。

### 智能提醒（可选）
- 下雨概率 &gt; 40%：提醒带伞 ☔
- 温差 &gt; 8°C：提醒增减衣物
- 高温 &gt; 33°C：提醒防暑 🌞
- 低温 &lt; 15°C：提醒保暖 ❄️

## 文件说明

| 文件 | 说明 |
|------|------|
| `weather.py` | 主程序：获取天气 → 解析数据 → 推送消息 |
| `.env.example` | 环境变量模板（复制为 `.env` 使用） |
| `.env` | 本地环境变量（存放真实 Webhook，**不上传**） |
| `.gitignore` | Git 忽略文件列表，防止敏感信息上传 |
| `.github/workflows/weather.yml` | GitHub Actions 定时任务配置（每天 UTC 5:00 运行） |
| `README.md` | 项目说明文档 |

## 常见问题

**Q: 推送没收到？**
- 检查 GitHub Actions 是否显示绿色勾（成功）
- 检查飞书机器人关键词是否设置为"天气"或"提醒"
- 检查企业微信机器人是否在群里
- 检查 GitHub Secrets 是否配置正确

**Q: 本地运行成功，但 GitHub Actions 失败？**
- 检查 Secrets 是否配置（Settings → Secrets and variables → Actions）
- 检查 Secrets 名称是否和代码里一致（区分大小写）
- 检查 Actions 日志（点进运行记录 → 展开 "Run weather check"）

**Q: 如何修改推送时间？**
- 修改 `.github/workflows/weather.yml` 中的 `cron` 时间
- 默认 `'0 5 * * *'` 是 UTC 5:00（北京 13:00），GitHub 可能延迟数小时
- 如需准时，建议使用外部定时服务（如 cron-job.org）触发

**Q: 天气数据准确吗？**
- 数据来自香港天文台官方 API，准确可靠
- 更新频率：每 10 分钟（实时数据）

**Q: 如何添加其他城市？**
- 本项目针对香港，如需其他城市需改用其他 API（如和风天气）
- 或修改 `weather.py` 中的 API 地址和参数

**Q: 飞书收不到但企微能收到？**
- 检查飞书机器人安全设置的关键词是否为"天气"或"提醒"
- 检查飞书机器人是否被停用（群设置 → 群机器人）
- 检查 `FEISHU_WEBHOOK_URL` 是否为最新地址

**Q: 如何关闭天气警报功能？**
- 编辑 `weather.py`，注释掉 `check_weather_warnings()` 相关代码
- 或删除 `.github/workflows/weather.yml` 中的相应触发器

**Q: 为什么显示的是明天的天气？**
- 代码自动获取明天（而非今天）的数据，方便提前准备
- 如需改为今天，修改 `weather.py` 中的日期索引

## 数据源

- **API**: [香港天文台开放数据](https://data.gov.hk/)
- **文档**: [HKO Open Data API Documentation](https://www.hko.gov.hk/en/abouthko/opendata_intro.htm)
- **特点**: 官方权威、免费、无需注册、实时更新

## 技术栈

- **语言**: Python 3.11
- **依赖**: `requests`, `python-dotenv`
- **部署**: GitHub Actions（定时任务）
- **推送**: 企业微信机器人 + 飞书机器人

## License

MIT