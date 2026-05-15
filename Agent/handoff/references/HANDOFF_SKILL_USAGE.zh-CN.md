# Handoff Skill 中文使用说明

这份文档说明如何使用 `handoff` skill，把一次长对话整理成可交接、可复用的项目上下文。

它的定位不是替代 Codex 自带的 compact，而是作为长期协作的可读检查点。

## 一句话判断

```text
compact 负责让当前会话继续跑。
handoff 负责让下一个会话接得准。
```

如果你还在同一个会话里连续推进任务，优先依赖 Codex 自带 compact。

如果你要跨天、换会话、换 agent、换模型，或者进入新的工作阶段，就应该创建或更新 handoff。

## 什么时候使用 handoff

建议在这些时机使用：

- 准备结束当前会话，之后还要继续同一个任务。
- 准备开启新 Codex 会话。
- 任务从调研进入实现，或从实现进入测试、发布。
- 刚刚做出关键设计决策。
- 发现了重要限制、坑点、失败测试、兼容性问题或被排除的方案。
- 当前对话探索了很多方向，噪音变多，想开一个干净的新会话继续。
- 准备手动 compact 前，希望先留下一个可读的检查点。

不建议在这些场景使用：

- 只是一个很小的 bugfix。
- 当前会话还很短、上下文很清晰。
- 所有重要信息已经完整写在 PRD、ADR、issue、commit、diff 或测试里。
- 只是想节省当前会话 token，这种情况更适合 compact。

## 推荐保存位置

不要长期依赖临时文件。长期配合时，建议把 handoff 放在稳定路径。

项目内通用路径：

```text
.codex/handoff.md
docs/ai-handoff.md
```

如果一个项目很大，也可以按主题拆分：

```text
.codex/handoff-crawler.md
.codex/handoff-ui.md
.codex/handoff-release.md
```

## 固定格式

默认使用这套格式：

```md
# AI Handoff

## Current Goal
当前目标，以及下一会话应该优先优化什么。

## Completed
已经完成的事情。尽量引用 commit、diff、PRD、计划、issue 或文件路径，不要复制大段内容。

## Key Decisions
关键决策、被排除的方案，以及为什么这样选择。

## Constraints
不能破坏的约束、兼容性限制、用户偏好、必须遵守的边界。

## Open Problems
还没解决的问题、已知风险、失败测试、阻塞点、不确定事项。

## Next Steps
下一会话建议按优先级执行的步骤。

## Useful References
相关文件、命令、URL、产物，以及建议下一会话使用的 skills。
```

## 当前会话中创建 handoff

可以直接使用这个提示词：

```text
使用 handoff skill。
请把当前会话整理成交接文档，写入：
.codex/handoff.md

下一会话目标：继续实现 <具体目标>。
请使用固定格式：
Current Goal、Completed、Key Decisions、Constraints、Open Problems、Next Steps、Useful References。
不要重复 PRD、计划、ADR、issue、commit 或 diff 中已有的内容，只引用路径或 URL。
```

项目内使用示例：

```text
使用 handoff skill。
请更新 .codex/handoff.md。

下一会话目标：继续修复新闻抓取任务的失败重试逻辑，并补充测试。
重点记录：
- 已经读过哪些模块
- 哪些方案被排除
- 当前失败的测试或命令
- 下一步最应该先看的文件
```

准备 compact 前使用：

```text
使用 handoff skill。
请先更新 .codex/handoff.md。

重点保留：
- 当前目标
- 已完成事项
- 关键决策
- 未完成事项
- 下一步

完成后我会再执行 compact。
```

## 新会话中恢复上下文

新会话开始时，可以这样说：

```text
我们从上个会话继续。
请先阅读 .codex/handoff.md，
再阅读其中 Useful References 引用的必要文件。

读完后，请先用 5 行以内复述当前状态和下一步，
然后继续执行 Next Steps。
```

针对具体项目：

```text
请从 .codex/handoff.md 接着做。
先读取 handoff 和其中引用的文件。
不要重新探索已经在 Key Decisions 里排除的方案。
请从 Next Steps 的第一项开始实施，并在完成后更新 handoff。
```

如果你想让新会话先校准而不是马上动手：

```text
请先阅读 .codex/handoff.md。
读完后只做三件事：
1. 复述当前目标
2. 列出你认为的下一步
3. 指出 handoff 里不清楚或可能过期的地方

先不要修改文件。
```

## 推荐工作流

长期项目可以按这个节奏使用：

1. 平时在同一会话里正常推进任务。
2. 上下文变长时，让 Codex compact 维持当前会话续航。
3. 到阶段边界时，更新 handoff。
4. 新会话先读取 handoff，再读取里面引用的文件。
5. 完成一个阶段后，再次更新 handoff。

一个比较稳的节奏：

```text
调研结束 -> 更新 handoff
实现前 -> 新会话读取 handoff
实现完成 -> 更新 handoff
测试前 -> compact 或新会话读取 handoff
发布前 -> 更新 handoff
任务完成 -> 清理或归档 handoff
```

## 维护原则

- handoff 要短，重点是让下一会话快速接上。
- 长期事实写入 handoff，临时推理不用写。
- 大段 PRD、ADR、issue、commit、diff 不要复制，只引用路径或 URL。
- 如果 handoff 和代码、测试、commit、项目文档冲突，优先相信代码和正式文档，并更新 handoff。
- 不要每做一个小动作就更新，优先在阶段边界更新。
- 任务结束后，把有价值的信息归档到 PR、issue、changelog、ADR 或正式文档里。

## 使用判断表

| 场景 | 推荐动作 |
|---|---|
| 同一会话继续做同一个任务，只是上下文变长 | 使用 compact |
| 今天做到一半，明天继续 | 更新 handoff |
| 要开新 Codex 会话 | 先读 handoff |
| 做了重要设计决策 | 更新 handoff |
| 探索了很多失败方向，想干净重启 | 更新 handoff，然后开新会话 |
| 重要信息已经在 PRD 或 ADR 里 | handoff 只引用这些文件 |
| 小型一次性修复 | 通常不需要 handoff |

## 最小可用模板

如果你只想快速生成一份最小 handoff，可以用：

```text
使用 handoff skill，写入 .codex/handoff.md。
请按固定格式总结当前会话，重点写清楚：
1. 当前目标
2. 已完成事项
3. 关键决策
4. 约束
5. 未解决问题
6. 下一步
7. 需要读取的文件或命令
```
