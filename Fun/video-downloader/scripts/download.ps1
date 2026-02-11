<#
.SYNOPSIS
    视频下载脚本 - 支持多平台视频下载和音频提取

.DESCRIPTION
    使用yt-dlp下载视频，支持YouTube、Bilibili、X等平台
    可选择提取音频为MP3格式

.PARAMETER Url
    视频URL地址

.PARAMETER OutputDir
    输出目录，默认为当前目录

.PARAMETER ExtractAudio
    是否提取音频

.PARAMETER AudioFormat
    音频格式 (mp3, m4a, wav, aac, flac, opus)

.PARAMETER Quality
    视频质量 (best, 1080, 720, 480)

.PARAMETER Proxy
    代理地址 (例如: http://127.0.0.1:7890)

.PARAMETER KeepVideo
    提取音频时是否保留视频文件

.EXAMPLE
    .\download.ps1 -Url "https://www.youtube.com/watch?v=xxx"
    
.EXAMPLE
    .\download.ps1 -Url "https://www.bilibili.com/video/BVxxx" -ExtractAudio -AudioFormat mp3
    
.EXAMPLE
    .\download.ps1 -Url "https://x.com/user/status/xxx" -Proxy "http://127.0.0.1:7890"
#>

param(
    [Parameter(Mandatory=$true, HelpMessage="视频URL地址")]
    [string]$Url,
    
    [Parameter(HelpMessage="输出目录")]
    [string]$OutputDir = ".",
    
    [Parameter(HelpMessage="是否提取音频")]
    [switch]$ExtractAudio,
    
    [Parameter(HelpMessage="音频格式")]
    [ValidateSet("mp3", "m4a", "wav", "aac", "flac", "opus")]
    [string]$AudioFormat = "mp3",
    
    [Parameter(HelpMessage="视频质量")]
    [ValidateSet("best", "1080", "720", "480", "360")]
    [string]$Quality = "best",
    
    [Parameter(HelpMessage="代理地址")]
    [string]$Proxy = "",
    
    [Parameter(HelpMessage="提取音频时保留视频")]
    [switch]$KeepVideo
)

# 检查yt-dlp是否安装
function Test-YtDlp {
    try {
        $null = Get-Command yt-dlp -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# 检查ffmpeg是否安装
function Test-FFmpeg {
    try {
        $null = Get-Command ffmpeg -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# 主函数
function Start-Download {
    # 检查依赖
    if (-not (Test-YtDlp)) {
        Write-Host "❌ 错误: yt-dlp 未安装" -ForegroundColor Red
        Write-Host "请运行: pip install yt-dlp" -ForegroundColor Yellow
        exit 1
    }
    
    if ($ExtractAudio -and -not (Test-FFmpeg)) {
        Write-Host "❌ 错误: FFmpeg 未安装 (音频提取需要)" -ForegroundColor Red
        Write-Host "请运行: winget install FFmpeg" -ForegroundColor Yellow
        exit 1
    }
    
    # 创建输出目录
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        Write-Host "📁 创建目录: $OutputDir" -ForegroundColor Cyan
    }
    
    # 构建命令参数
    $args = @()
    
    # 输出模板
    $outputTemplate = Join-Path $OutputDir "%(title)s.%(ext)s"
    $args += @("-o", "`"$outputTemplate`"")
    
    # 视频质量
    switch ($Quality) {
        "best" { 
            $args += @("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
        }
        "1080" { 
            $args += @("-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]")
        }
        "720" { 
            $args += @("-f", "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]")
        }
        "480" { 
            $args += @("-f", "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]")
        }
        "360" { 
            $args += @("-f", "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]")
        }
    }
    
    # 代理
    if ($Proxy -ne "") {
        $args += @("--proxy", $Proxy)
        Write-Host "🌐 使用代理: $Proxy" -ForegroundColor Cyan
    }
    
    # 音频提取
    if ($ExtractAudio) {
        $args += @("-x", "--audio-format", $AudioFormat, "--audio-quality", "0")
        if ($KeepVideo) {
            $args += "-k"
        }
        Write-Host "🎵 将提取音频: $AudioFormat 格式" -ForegroundColor Cyan
    }
    
    # 添加URL
    $args += "`"$Url`""
    
    # 显示信息
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║                    📥 Video Downloader                         ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "🔗 URL: $Url" -ForegroundColor Green
    Write-Host "📂 输出目录: $OutputDir" -ForegroundColor Green
    Write-Host "📺 质量: $Quality" -ForegroundColor Green
    Write-Host ""
    
    # 执行下载
    Write-Host "⏳ 开始下载..." -ForegroundColor Yellow
    Write-Host ""
    
    $command = "yt-dlp " + ($args -join " ")
    Write-Host "执行命令: $command" -ForegroundColor DarkGray
    Write-Host ""
    
    Invoke-Expression $command
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ 下载完成!" -ForegroundColor Green
        Write-Host "📂 文件保存至: $OutputDir" -ForegroundColor Green
    }
    else {
        Write-Host ""
        Write-Host "❌ 下载失败，请检查URL和网络连接" -ForegroundColor Red
    }
}

# 执行
Start-Download
