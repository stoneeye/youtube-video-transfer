# YouTube to Bilibili 搬运项目计划

## 1. 项目目标
构建一个自动化工具，监控指定的 YouTube 频道，自动下载新视频并上传到 Bilibili。

## 2. 技术栈
- **语言**: Python 3.10+
- **下载**: `yt-dlp` (最强大的 YouTube 下载工具)
- **上传**: `bilibili-api-python` (功能完善的 B 站 API 库)
- **数据存储**: `SQLite` (轻量级，无需额外配置)
- **配置**: `YAML` (易读易写)
- **日志**: `logging` 标准库

## 3. 核心模块设计
1.  **Config Manager**: 读取 `config.yaml`，管理 Cookies、频道列表、下载路径等。
2.  **DB Manager**: 管理 `history.db`，记录已处理的视频 ID，防止重复搬运。
3.  **YouTube Downloader**: 封装 `yt-dlp`，负责获取视频信息、下载视频和封面。
4.  **Bilibili Uploader**: 封装上传逻辑，处理标题、简介、标签、分区等。
5.  **Main Scheduler**: 主循环，定期轮询，协调下载和上传流程。

## 4. 实施步骤
1.  **初始化**: 创建项目结构，配置依赖 (`requirements.txt`)。
2.  **配置与数据库**: 实现配置读取和数据库初始化。
3.  **下载模块**: 实现 YouTube 视频下载功能。
4.  **上传模块**: 实现 Bilibili 视频上传功能（需要用户提供 Cookies）。
5.  **主逻辑与调度**: 串联流程，实现自动轮询。
6.  **测试与文档**: 编写使用说明 `README.md`。

## 5. 目录结构
```
video-transfer/
├── config/
│   ├── config.yaml.example
│   └── cookies.json (用户存放)
├── data/
│   └── history.db
├── downloads/
├── src/
│   ├── __init__.py
│   ├── config_loader.py
│   ├── database.py
│   ├── downloader.py
│   ├── uploader.py
│   └── main.py
├── requirements.txt
├── README.md
└── PLAN.md
```
