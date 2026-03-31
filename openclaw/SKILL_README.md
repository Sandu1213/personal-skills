# SKILL README（按用处整理）

> 更新时间：2026-03-28  
> 说明：以下为当前可用 skills，按实际用途分组，便于快速选择。

---

## 1) 信息获取 / 搜索 / 抓取

- **tavily-search**：联网检索信息（搜索入口，找链接与摘要）。
- **markdown-proxy**：把网页转成干净 Markdown（含登录墙/社交平台页面）。
- **defuddle**：提取网页正文，去噪省 token。
- **scrapling-official**：复杂网站抓取、反爬场景、爬虫开发。
- **weather**：天气查询与预报。

---

## 2) 内容总结 / 研读 / 输出结构化结论

- **briefing-factory**：把文章/资料流整理成稳定结构的简报、摘要、洞察。
- **english-tutor**：英文纠错、润色、表达优化。
- **weekly-report**：按模板生成周报并归档 Markdown。

---

## 3) Obsidian 知识管理

- **obsidian**：Obsidian vault 通用操作（读写、组织）。
- **obsidian-cli**：通过 CLI 深度操作 Obsidian（含插件调试）。
- **obsidian-markdown**：生成/编辑 Obsidian 风格 Markdown（wikilink、callout、frontmatter）。
- **obsidian-bases**：创建/编辑 `.base` 数据视图。
- **json-canvas**：创建/编辑 `.canvas` 画布文件。
- **web-to-obsidian**：网页内容抓取后直接保存到 Obsidian。
- **x-to-obsidian**：X/Twitter 帖子保存到 Obsidian。

---

## 4) Feishu / 飞书协作

- **feishu-doc**：飞书文档读写（docx）。
- **feishu-drive**：飞书云盘文件/文件夹管理。
- **feishu-wiki**：飞书知识库（wiki）导航与节点操作。
- **feishu-perm**：飞书权限与协作者管理。

---

## 5) 音视频处理

- **video-downloader**：下载视频（yt-dlp）。
- **video-frames**：视频抽帧/短片段裁切（ffmpeg）。
- **video-transcript-bilingual**：视频转写并输出双语（原文+英文）。
- **gemini-image-gen**：基于文案生成图片或对图片进行编辑。

---

## 6) 技能开发 / 质量 / 安全治理

- **skill-creator**：创建与整理技能（结构与规范）。
- **skill-creator-plus**：技能增强工作流（eval / benchmark / A-B / description 优化）。
- **skill-vetter**：技能安全审查（安装前风险检查）。
- **clawhub**：从 ClawHub 搜索、安装、更新、发布技能。
- **frontend-design**: 设计更好看的前端页面(https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design)

---

## 7) 系统运维 / 平台连接

- **healthcheck**：主机安全与风险姿态检查、加固建议。
- **node-connect**：OpenClaw 节点配对/连接故障排查（含移动端）。
- **model-usage**：按模型统计用量与费用（CodexBar 相关）。
- **discord**：Discord 渠道操作规范与最佳实践。

---

## 8) 交互风格 / 思维流程（元技能）

- **grill-me**：高强度追问，压力测试方案与设计。
- **tdd**：测试驱动开发（Red-Green-Refactor）。
- **Self-Improving Agent (With Self-Reflection)**：自我反思与改进流程。

---

## 快速选择建议

- 想**找资料**：先 `tavily-search`，再 `markdown-proxy/defuddle` 深读。  
- 想**沉淀到知识库**：网页用 `web-to-obsidian`，X 帖子用 `x-to-obsidian`。  
- 想**做技能**：先 `skill-vetter`（安全审查），再 `skill-creator-plus`（开发与评测）。  
- 想**做飞书协作**：文档 `feishu-doc`，网盘 `feishu-drive`，知识库 `feishu-wiki`，权限 `feishu-perm`。
