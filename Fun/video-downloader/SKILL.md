---
name: Video Downloader
version: 1.0.0
description: 下载视频文件并支持音频提取，支持YouTube、Bilibili(B站)、X(Twitter)等主流平台.下载的视频保存在videos文件夹下,音频保存在audio文件夹下.
---

# Video Downloader Skill

这是一个用于下载视频并提取音频的技能，支持多个主流视频平台。

## 前置依赖

在使用此技能前，请确保已安装以下工具：

### 1. yt-dlp (核心下载工具)
yt-dlp是youtube-dl的分支，支持更多平台和更好的性能。

```powershell
# 使用pip安装 (推荐)
pip install yt-dlp

# 或使用winget安装
winget install yt-dlp

# 或使用scoop安装
scoop install yt-dlp
```

### 2. FFmpeg (音频提取必需)
```powershell
# 使用winget安装
winget install FFmpeg

# 或使用scoop安装
scoop install ffmpeg

# 或使用chocolatey安装
choco install ffmpeg
```

## 使用说明

当用户请求下载视频时，按以下步骤操作：

### 步骤1：确认视频URL和需求
向用户确认：
- 视频的URL地址
- 是否需要提取音频
- 期望的输出质量（如：最佳质量、1080p、720p等）
- 保存位置（默认：当前目录videos文件夹下或用户指定目录）

### 步骤2：下载视频

#### 基本下载命令
```powershell
# 下载最佳质量视频
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "%(title)s.%(ext)s" "<视频URL>"

# 下载指定分辨率 (例如1080p)
yt-dlp -f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]" -o "%(title)s.%(ext)s" "<视频URL>"

# 仅查看可用格式（不下载）
yt-dlp -F "<视频URL>"
```

#### 各平台特殊说明

**YouTube:**
```powershell
# 标准下载
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" "https://www.youtube.com/watch?v=VIDEO_ID"

# 下载整个播放列表
yt-dlp -f "bestvideo+bestaudio" --playlist-items 1-10 "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

**Bilibili (B站):**
```powershell
# 标准下载
yt-dlp -f "bestvideo+bestaudio/best" "https://www.bilibili.com/video/BV1xxxxxxxxxx"

# 下载分P视频
yt-dlp -f "bestvideo+bestaudio/best" --playlist-items 1-5 "https://www.bilibili.com/video/BV1xxxxxxxxxx"

# 如果需要登录的视频，使用cookies
yt-dlp --cookies-from-browser chrome "https://www.bilibili.com/video/BV1xxxxxxxxxx"
```

**X (Twitter):**
```powershell
# 标准下载
yt-dlp -f "best" "https://x.com/user/status/TWEET_ID"

# 或使用twitter.com域名
yt-dlp -f "best" "https://twitter.com/user/status/TWEET_ID"
```

### 步骤3：提取音频

```powershell
# 下载时直接提取音频 (MP3格式)
yt-dlp -x --audio-format mp3 --audio-quality 0 -o "%(title)s.%(ext)s" "<视频URL>"

# 下载时直接提取音频 (其他格式: m4a, wav, aac, flac, opus)
yt-dlp -x --audio-format m4a --audio-quality 0 -o "%(title)s.%(ext)s" "<视频URL>"

# 从已下载的视频中提取音频
ffmpeg -i "input_video.mp4" -vn -acodec libmp3lame -q:a 0 "output_audio.mp3"

# 提取为高品质WAV
ffmpeg -i "input_video.mp4" -vn "output_audio.wav"

# 提取为AAC
ffmpeg -i "input_video.mp4" -vn -acodec aac -b:a 256k "output_audio.aac"
```

### 步骤4：高级选项

#### 自定义输出文件名
```powershell
# 使用模板
yt-dlp -o "%(uploader)s - %(title)s.%(ext)s" "<视频URL>"

# 指定输出目录
yt-dlp -o "C:/Videos/%(title)s.%(ext)s" "<视频URL>"
```

#### 使用代理
```powershell
# HTTP代理
yt-dlp --proxy "http://127.0.0.1:7890" "<视频URL>"

# SOCKS5代理
yt-dlp --proxy "socks5://127.0.0.1:1080" "<视频URL>"
```

#### 下载字幕
```powershell
# 下载自动生成的字幕
yt-dlp --write-auto-sub --sub-lang "zh-Hans,en" "<视频URL>"

# 下载嵌入字幕
yt-dlp --embed-subs --sub-lang "zh-Hans,en" "<视频URL>"
```

#### 限速下载
```powershell
# 限制下载速度为1MB/s
yt-dlp -r 1M "<视频URL>"
```

## 常用组合命令

### 下载视频+提取音频（一站式）
```powershell
# 同时保存视频和音频
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" -o "%(title)s.%(ext)s" --extract-audio --audio-format mp3 --audio-quality 0 -k "<视频URL>"
```
注意：`-k` 参数保留原始视频文件

### 批量下载
```powershell
# 从文件读取URL列表（每行一个URL）
yt-dlp -a urls.txt -o "%(title)s.%(ext)s"
```

## 错误处理

### 常见问题及解决方案

1. **"Video unavailable"**
   - 检查URL是否正确
   - 视频可能需要登录：使用 `--cookies-from-browser chrome` 参数

2. **下载速度慢**
   - 尝试使用代理
   - 降低视频质量：`-f "bestvideo[height<=720]+bestaudio/best"`

3. **"ffmpeg not found"**
   - 确保FFmpeg已安装并添加到系统PATH

4. **B站下载失败**
   - 尝试更新yt-dlp：`pip install -U yt-dlp`
   - 使用cookies：`--cookies-from-browser edge`

5. **X/Twitter下载失败**
   - 部分推文可能受保护或已删除
   - 尝试使用cookies进行认证

## 支持的平台列表

yt-dlp支持上千个网站，常用的包括：
- YouTube
- Bilibili (哔哩哔哩)
- X (Twitter)
- TikTok
- Instagram
- Facebook
- Twitch
- Vimeo
- 抖音
- 西瓜视频
- 小红书
- 等等...

查看完整支持列表：
```powershell
yt-dlp --list-extractors
```

## 输出目录结构

建议将下载的文件保存到用户指定目录，默认结构：
```
<用户指定目录>/
├── videos/          # 视频文件
│   ├── video1.mp4
│   └── video2.mp4
└── audio/           # 提取的音频
    ├── video1.mp3
    └── video2.mp3
```

## 示例对话

**用户**: 帮我下载这个YouTube视频 https://www.youtube.com/watch?v=xxx 并提取音频

**助手响应**:
1. 确认视频URL和需求
2. 创建输出目录（如果需要）
3. 执行下载命令
4. 执行音频提取
5. 返回文件位置信息
