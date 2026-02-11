# Video Downloader Skill

一个强大的视频下载技能，支持从YouTube、Bilibili(B站)、X(Twitter)等主流平台下载视频并提取音频。

## ✨ 功能特性

- 🎬 **多平台支持**: YouTube、Bilibili、X/Twitter、TikTok、Instagram等上千个网站
- 🎵 **音频提取**: 支持提取MP3、AAC、FLAC、WAV等多种音频格式
- 📺 **质量选择**: 支持选择不同的视频质量（4K、1080p、720p等）
- 📝 **字幕下载**: 支持下载和嵌入字幕
- 🚀 **代理支持**: 支持HTTP/SOCKS5代理

## 🛠 前置依赖

### 必需工具

| 工具 | 用途 | 安装方式 |
|------|-----|---------|
| yt-dlp | 视频下载核心 | `pip install yt-dlp` |
| FFmpeg | 音频提取/视频处理 | `winget install FFmpeg` |

## 📖 快速开始

### 下载视频
```powershell
yt-dlp -f "best" "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 提取音频
```powershell
yt-dlp -x --audio-format mp3 "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 下载并提取音频
```powershell
yt-dlp -f "best" -x --audio-format mp3 -k "https://www.youtube.com/watch?v=VIDEO_ID"
```

## 📂 文件结构

```
videofree/
├── SKILL.md          # 技能详细说明
├── README.md         # 本文件
└── scripts/          # 辅助脚本
    └── download.ps1  # PowerShell下载脚本
```

## 🔗 相关链接

- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg官网](https://ffmpeg.org/)