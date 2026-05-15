# Handoff Skill Usage Guide

This guide describes how to use the `handoff` skill as a long-term project memory mechanism alongside Codex's built-in context compaction.

## What It Is For

Use `handoff` when work needs to survive a session boundary: a new Codex thread, a different agent, a different model, another day of work, or a major phase change.

Use Codex built-in compact when you are staying in the same thread and only need to reduce context pressure.

Short rule:

```text
Compact keeps the current session alive.
Handoff helps the next session start correctly.
```

## When To Create A Handoff

Create or update a handoff when:

- You are about to end the current session.
- You are about to open a new session.
- The task moves from research to implementation, implementation to testing, or testing to release.
- A key decision was made and losing it would cause rework.
- You found a trap, constraint, failing test, fragile API, or rejected approach.
- The conversation has become noisy and you want a clean restart.
- You are about to manually compact a long-running conversation and want a readable checkpoint first.

Do not create one just because a tiny local bugfix took a few turns. For small same-session work, compact or ordinary conversation context is enough.

## Recommended File Location

For ongoing work in a workspace, prefer a stable project file instead of a temporary file:

```text
.codex/handoff.md
docs/ai-handoff.md
```

For a specific topic inside a large project, use a topic-specific file:

```text
.codex/handoff-crawler.md
.codex/handoff-ui.md
.codex/handoff-release.md
```

Temporary files are useful for one-off transfers, but stable files are better for long-term collaboration.

## Default Handoff Format

Use this structure:

```md
# AI Handoff

## Current Goal
Current objective and what the next session should optimize for.

## Completed
Already completed work. Reference commits, diffs, PRDs, plans, issues, or files instead of copying their contents.

## Key Decisions
Important choices, rejected approaches, and why they matter.

## Constraints
Non-negotiable requirements, compatibility limits, user preferences, and things the next agent must not break.

## Open Problems
Unresolved questions, known risks, failing tests, blockers, and uncertainty.

## Next Steps
Recommended next actions in priority order.

## Useful References
Relevant files, commands, URLs, artifacts, and suggested skills for the next session.
```

## Create A Handoff In The Current Session

Use a prompt like this:

```text
Use the handoff skill.
Summarize the current conversation into a handoff document and write it to:
.codex/handoff.md

Next session goal: continue implementing <specific goal>.
Use the fixed format:
Current Goal, Completed, Key Decisions, Constraints, Open Problems, Next Steps, Useful References.
Do not duplicate content already captured in PRDs, plans, ADRs, issues, commits, or diffs. Reference paths or URLs instead.
```

Project-specific example:

```text
Use the handoff skill.
Update .codex/handoff.md.

Next session goal: continue fixing the crawler retry logic and add tests.
Focus on:
- Which modules were already inspected
- Which approaches were rejected
- Current failing tests or commands
- Which files should be read first next time
```

Before a manual compact:

```text
Use the handoff skill and update .codex/handoff.md first.
Preserve the current goal, completed work, key decisions, unfinished items, and next steps.
After that, I will run compact.
```

## Resume From A Handoff In A New Session

Start the next session with:

```text
We are continuing from the previous session.
Please read .codex/handoff.md first,
then read the necessary files referenced in Useful References.

After reading, summarize the current state and next step in 5 lines or fewer,
then continue with Next Steps.
```

For a project-specific continuation:

```text
Continue from .codex/handoff.md.
Read the handoff and the files it references.
Do not re-explore approaches already rejected in Key Decisions.
Start from the first item in Next Steps and update the handoff after finishing.
```

## Maintenance Rules

- Keep the handoff short enough to read quickly.
- Put durable facts in the handoff, not temporary reasoning.
- Reference artifacts by path or URL instead of copying large content.
- Update the handoff at phase boundaries, not after every tiny action.
- If the handoff conflicts with source code, tests, commits, or project docs, trust the primary artifact and update the handoff.
- When a task finishes, either archive the handoff content into a PR, issue, changelog, or clear it for the next objective.

## Practical Decision Table

| Situation | Use |
|---|---|
| Same thread, same task, context getting long | Codex compact |
| End of day, continue tomorrow | Handoff |
| Start a new Codex conversation | Read handoff first |
| Major design decision made | Update handoff |
| Lots of noisy exploration happened | Handoff, then start clean |
| Important details already live in PRD or ADR | Reference those files |
| Small one-off fix | No handoff needed |
