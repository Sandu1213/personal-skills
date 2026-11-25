# 第三方外部 Skill 索引

这个目录不是可直接加载的 skill 集合，而是第三方 skill 的索引表。

用途：

- 记录值得关注或已经迁移过的外部 skill。
- 保存原始仓库、具体路径、适用场景和迁移状态。
- 方便之后手动安装、二次改造或迁移到 `Agent/`、`Work/`、`Fun/`。
- 避免把还没有真正整理成本地 skill 的外部资料混进可加载目录。

原则上这里优先维护索引记录。若临时保留完整第三方仓库快照，也应视为上游参考或迁移材料，不作为本仓库的本地 skill 入口。

## 状态说明

| 状态 | 含义 |
|---|---|
| `候选` | 只是记录，尚未安装或迁移 |
| `已迁移` | 已改造成当前仓库里的本地 skill |
| `已安装` | 已安装到本机 AI 工具，但未必进入本仓库 |
| `观察中` | 值得关注，但还不确定是否长期使用 |
| `放弃` | 调研后暂不采用，保留原因便于以后判断 |

## 外部 Skill 清单

| Skill | 来源仓库 | 原始路径 / URL | 使用场景 | 建议归类 | 状态 | 备注 |
|---|---|---|---|---|---|---|
| handoff | `mattpocock/skills` | [skills/in-progress/handoff](https://github.com/mattpocock/skills/tree/733d312884b3878a9a9cff693c5886943753a741/skills/in-progress/handoff) | 将长对话整理成交接文档，方便新会话、新 agent 或未来自己接续任务 | `Agent/handoff` | `已迁移` | 当前仓库已维护改造版：[Agent/handoff](../Agent/handoff/) |
| baoyu-skills | `JimLiu/baoyu-skills` | [github.com/JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) | 内容生成与发布、AI 生图、图文处理、URL/X 转 Markdown、小红书/微信/X 发布辅助等 Claude Code skills 集合 | 按需手动安装；如长期使用再迁移单个子 skill 到 `Work/...` | `候选` | 安装：`npx skills add jimliu/baoyu-skills`；Claude Code 插件市场：`/plugin marketplace add jimliu/baoyu-skills`；按插件安装：`/plugin install content-skills@baoyu-skills`、`/plugin install ai-generation-skills@baoyu-skills`、`/plugin install utility-skills@baoyu-skills` |
| remotion-best-practices | `remotion-dev/skills` | [skills/remotion](https://github.com/remotion-dev/skills/tree/main/skills/remotion) | 使用 Remotion、React、动画、字幕、音频、视频渲染等制作程序化视频 | `External`，如长期使用可迁移到 `Fun/remotion` | `候选` | 推荐安装命令：`npx skills add https://github.com/remotion-dev/skills --skill remotion-best-practices` |
| research | `mattpocock/skills` | [skills/engineering/research](https://github.com/mattpocock/skills/tree/main/skills/engineering/research) | 调研问题、收集文档与 API 事实，委派带来源的资料阅读 | `External`，如需本地化可迁移到 `Agent/research` | `已安装` | 安装：`npx skills add mattpocock/skills --skill research` |
| diagnosing-bugs | `mattpocock/skills` | [skills/engineering/diagnosing-bugs](https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnosing-bugs) | 诊断报错、失败、异常或变慢的行为，先复现再定位根因 | `External`，如需本地化可迁移到 `Work/diagnosing-bugs` | `已安装` | 安装：`npx skills add mattpocock/skills --skill diagnosing-bugs` |
| agent-reach | `Panniantong/Agent-Reach` | [github.com/Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | 网页搜索与读取，覆盖小红书、微博、推特、B站、Reddit、GitHub、YouTube、公众号、RSS 等平台 | `External` | `已安装` | 依赖 `agent-reach` CLI，首次运行 `agent-reach install --env=auto` 安装工具 |

## 新增记录模板

新增外部 skill 时，在上表增加一行：

```markdown
| skill-name | `owner/repo` | [path-or-url](https://github.com/owner/repo/tree/ref/path/to/skill) | 适用场景 | `Agent/...` / `Work/...` / `Fun/...` | `候选` | 备注 |
```

## 手动安装或迁移建议

安装或迁移前，先确认三件事：

1. 这个 skill 是否真的会长期使用。
2. 原始 skill 是否需要本地化改造，例如路径、语言、默认格式、工作区习惯。
3. 它应该进入 `Agent/`、`Work/` 还是 `Fun/`。

常用提示词：

```text
请查看 External/README.md 中的 <skill-name> 记录，
读取它的原始仓库和路径，
判断是否适合迁移到本仓库。
先给出迁移建议，不要直接修改文件。
```

如果已经决定迁移：

```text
请根据 External/README.md 中的 <skill-name> 记录，
把它迁移到建议归类目录下，
保留必要的 SKILL.md，
并把详细说明放入 references/。
```
