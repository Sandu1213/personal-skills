---
name: handoff
description: Compact the current conversation into a handoff document for another agent or future session to pick up. Trigger when the user says handoff, 交接, 会话交接, 上下文交接, or asks to continue work in a new session.
argument-hint: "What will the next session be used for?"
---

# Handoff

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

If the user specifies an output path, save it there. Otherwise, save it to a path produced by `mktemp -t handoff-XXXXXX.md` when available. Read the file before you write to it if it already exists.

## Default Structure

Use this structure unless the user asks for a different one:

```md
# AI Handoff

## Current Goal
The active objective and what the next session should optimize for.

## Completed
What has already been finished. Reference commits, diffs, plans, PRDs, issues, or files instead of duplicating their contents.

## Key Decisions
Important choices, rejected approaches, and the reasons behind them.

## Constraints
Non-negotiable requirements, compatibility limits, user preferences, and things the next agent must not break.

## Open Problems
Unresolved questions, known risks, failing tests, blockers, or uncertainty.

## Next Steps
The recommended next actions in priority order.

## Useful References
Relevant files, commands, URLs, artifacts, and suggested skills for the next session.
```

## Instructions

1. Ask for an output path only if the user did not provide one and a stable handoff location is important for the task.
2. Prefer stable project paths such as `.codex/handoff.md`, `docs/ai-handoff.md`, or a project-specific `.codex/handoff-<topic>.md` over temporary files for long-running work.
3. If the user passed arguments, treat them as a description of what the next session will focus on and tailor the handoff accordingly.
4. Suggest the skills to be used, if any, by the next session.
5. Do not duplicate content already captured in other artifacts such as PRDs, plans, ADRs, issues, commits, or diffs. Reference them by path, command, commit hash, or URL instead.
6. Keep the handoff concise enough for a new session to read quickly.

## References

- Read `references/HANDOFF_SKILL_USAGE.zh-CN.md` when the user wants Chinese usage guidance, invocation examples, or long-term workflow standards.
- Read `references/HANDOFF_SKILL_USAGE.md` when the user wants English usage guidance, invocation examples, or long-term workflow standards.

## Examples

Create a workspace handoff:

```text
使用 handoff skill。
请把当前会话整理成交接文档，写入：
D:\codex\research\.codex\handoff.md

下一会话目标：继续实现 <具体目标>。
```

Resume from a handoff:

```text
请先阅读 D:\codex\research\.codex\handoff.md，
再阅读其中 Useful References 引用的必要文件。
读完后用 5 行以内复述当前状态和下一步，然后继续执行 Next Steps。
```
