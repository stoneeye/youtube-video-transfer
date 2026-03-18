# YouTube to Bilibili Auto Transfer

这是一个自动化的搬运工具，旨在帮助你从 YouTube 搬运视频到 Bilibili。

## 功能特性
- 自动监控指定的 YouTube 频道
- 使用 `yt-dlp` 高质量下载视频
- 自动上传到 Bilibili 并填写元数据
- 记录搬运历史，防止重复搬运
- 支持定时任务 (默认每小时检查一次)

## 快速开始

1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
    *注意: 本项目依赖 FFmpeg 进行音视频合并。你可以运行项目根目录下的 `.\install_ffmpeg.ps1` 脚本自动下载并配置到 `bin/` 目录中，代码已支持自动识别。*

2.  **配置**:
    复制 `config/config.yaml.example` 为 `config/config.yaml` 并填入你的配置信息。

    **获取 Bilibili Cookies**:
    1. 在浏览器登录 Bilibili。
    2. 按 F12 打开开发者工具，进入 Application (应用) -> Cookies。
    3. 找到 `SESSDATA`, `bili_jct`, `DedeUserID` 这三个值。
    4. 填入 `config.yaml` 的 `bilibili` 部分。

    **配置 YouTube 频道**:
    在 `config.yaml` 中添加你想搬运的频道 URL 和对应的 B 站分区 ID (tid)。
    *例如: 游戏分区 ID 为 17。*

3.  **运行**:
    ```bash
    # 确保在项目根目录下
    set PYTHONPATH=.
    python src/main.py
    ```
    或者直接:
    ```bash
    python -m src.main
    ```

## 目录结构
- `config/`: 配置文件
- `data/`: 数据库文件 (SQLite)
- `downloads/`: 临时下载目录
- `src/`: 源代码
  - `downloader.py`: YouTube 下载逻辑
  - `uploader.py`: Bilibili 上传逻辑
  - `database.py`: 数据库模型
  - `main.py`: 主程序和调度器

## 注意事项
- 请遵守 Bilibili 的投稿规范和版权规定。
- 搬运视频建议选择“转载”并在简介中标注原作者和来源。
- `yt-dlp` 更新较快，如果下载失败，请尝试更新 `yt-dlp`: `pip install -U yt-dlp`。
