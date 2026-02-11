# 🧰 个人小助手 Skill 合集

> 基于 AI Agent 的个人技能库，按 **工作 (Work)** 和 **休闲 (Fun)** 两大类组织，支持自定义扩展。

---

## 📂 目录结构

```
personal-skills/
├── Work/          # 工作类技能
└── Fun/           # 休闲类技能
```

---

## 💼 Work — 工作类技能

| Skill | 触发关键字 | 说明 |
|-------|-----------|------|
| [weekly-report](Work/weekly-report/) | `weekly report` | 周报生成：提供工作内容，自动按模板生成周报 |
| [baoyu-skills](Work/baoyu-skills/) | `wechat`、`小红书`、`x` | 多平台内容辅助工具，提供生图及发布功能 |


## 🎮 Fun — 休闲类技能

| Skill | 触发关键字 | 说明 |
|-------|-----------|------|
| [video-downloader](Fun/video-downloader/) | `下载视频`、`download video` | 支持 YouTube/B站/X 等平台视频下载及音频提取 |
| [wallpaper-generator](Fun/wallpaper-generator/) | `生成壁纸`、`wallpaper` | 输入主题，生成6张适配主流手机的壁纸 |
| [remotion-skills](Fun/remotion-skills/) | `remotion`、`React video` | 基于 React 的 Remotion 视频制作最佳实践 |


---

## 🚀 快速开始

每个 skill 目录下都包含一个 `SKILL.md` 文件，描述了：
- **触发条件**：什么时候使用该技能
- **使用步骤**：详细的操作流程
- **前置依赖**：需要安装的工具（如有）

## ➕ 添加新 Skill

参见 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何扩展新技能。
