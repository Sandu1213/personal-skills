# 🧰 个人小助手 Skill 合集

> 基于 AI Agent 的个人技能库，按 **Agent 协作**、**工作 (Work)**、**休闲 (Fun)** 三类组织，另设 **External** 索引用于记录第三方外部 skills。

---

## 📂 目录结构

```
personal-skills/
├── Agent/                          # Agent 协作、上下文管理、技能维护
│   └── handoff/
├── External/                       # 第三方外部 skill 索引，不是可直接加载的 skill
├── Work/                           # 工作类技能
│   ├── growth/
│   ├── local-review/
│   ├── qa-review/
│   └── weekly-report/
└── Fun/                            # 休闲类技能
    ├── english_optimization_assistant/
    ├── video-downloader/
    └── wallpaper-generator/
```

---

## 🧠 Agent — AI 协作类技能

| Skill | 触发关键字 | 直接调用示例 | 说明 |
|-------|-----------|-------------|------|
| [handoff](Agent/handoff/) | `handoff`、`交接`、`上下文交接` | `使用 handoff skill，更新 .codex/handoff.md` | 会话交接：将长对话整理成可读检查点，方便新会话或新 agent 接续 |

## 🌐 External — 第三方外部 Skill 索引

| 索引 | 内容 | 用途 |
|------|------|------|
| [External/README.md](External/README.md) | 第三方 skill 名称、来源仓库、原始路径、使用场景、建议归类、迁移状态 | 方便后续调研、手动安装、迁移和维护 |

`External/` 不是可直接触发的 skill 目录，不要求包含 `SKILL.md`。它只是外部 skill 的清单和迁移台账。

## 💼 Work — 工作类技能

| Skill | 触发关键字 | 直接调用示例 | 说明 |
|-------|-----------|-------------|------|
| [weekly-report](Work/weekly-report/) | `weekly report`、`生成周报` | `使用 weekly-report skill，帮我生成本周周报` | 周报生成：提供工作内容，自动按模板生成周报 |
| [local-review](Work/local-review/) | `review current changes`、`评审代码`、`评审 PR` | `使用 local-review skill，review 当前工作区改动` | 代码评审：工作区 / commit / PR 分级 findings 与通过结论 |
| [qa-review](Work/qa-review/) | 复杂交付、质量标准、迭代验证 | `使用 qa-review skill，验收这个网站改版` | 复杂交付质量对齐：建立领域标准、迭代验证、便于人工审核的呈现 |


## 🎮 Fun — 休闲类技能

| Skill | 触发关键字 | 直接调用示例 | 说明 |
|-------|-----------|-------------|------|
| [video-downloader](Fun/video-downloader/) | `下载视频`、`download video` | `使用 video-downloader skill，下载这个视频链接` | 支持 YouTube/B站/X 等平台视频下载及音频提取 |
| [wallpaper-generator](Fun/wallpaper-generator/) | `生成壁纸`、`wallpaper` | `使用 wallpaper-generator skill，生成赛博朋克城市壁纸` | 输入主题，生成6张适配主流手机的壁纸 |


---

## 🚀 快速开始

每个 skill 目录下都包含一个 `SKILL.md` 文件，描述了：
- **触发条件**：什么时候使用该技能
- **使用步骤**：详细的操作流程
- **前置依赖**：需要安装的工具（如有）

## 🗣️ 如何调用

如果 skill 已安装到当前 AI 工具中，直接点名即可：

```text
使用 handoff skill，更新 .codex/handoff.md。
```

如果 skill 只存在于本仓库中，还没有安装到当前工具，可以让 agent 先读取对应文件：

```text
请先读取 Agent/handoff/SKILL.md，然后按这个 skill 的流程执行。
```

如果要查找或迁移第三方外部 skill，可以先读取外部索引：

```text
请先阅读 External/README.md，找出适合当前任务的第三方 skill，并给出安装或迁移建议。
```

`handoff` 的详细使用说明：

- [中文说明](Agent/handoff/references/HANDOFF_SKILL_USAGE.zh-CN.md)
- [English guide](Agent/handoff/references/HANDOFF_SKILL_USAGE.md)

新会话恢复 handoff 时，可以这样说：

```text
请先阅读 .codex/handoff.md，再读取其中 Useful References 引用的必要文件。
读完后用 5 行以内复述当前状态和下一步，然后继续执行 Next Steps。
```

## ➕ 添加新 Skill

参见 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何扩展新技能。
