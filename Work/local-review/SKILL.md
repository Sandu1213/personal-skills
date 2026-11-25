---
name: local-review
description: Review current workspace code changes, commits or ranges, and GitHub pull requests. Use when the user asks "review current changes", "review my modifications", "代码 review", "评审代码", "评审当前代码", "审一下改动", "评审 commit", "评审 PR", "这个能合吗", provides a GitHub PR or commit link for a review or approval decision, asks whether a change is ready to approve or deliver, or explicitly asks to submit the review verdict to a PR as Approve or Request changes. Default to the local workspace; a PR is optional. Produces severity-ranked findings, per-file coverage, impact analysis, verification evidence, delivery-gate status, and a deterministic pass, block, or unverified recommendation. Do not use when the sole outcome is implementing fixes, explaining architecture without a change set, ongoing CI monitoring, or writing PR descriptions or changelogs.
metadata:
  version: 3.15.1
---

# Local Review

Review the code the user has actually changed and decide whether the changed functionality is correct, safe, complete, and ready to proceed. A GitHub pull request is one possible input, not a prerequisite.

## Important

- Default to reviewing the current workspace (uncommitted changes plus unpushed commits) when the user does not provide a PR, commit, range, or explicit file list.
- Review both the intended functionality and every code change in scope. Trace production paths instead of judging the diff in isolation.
- Treat staged, unstaged, and relevant untracked files as separate evidence. A build that succeeds only because of an untracked dependency does not prove the commit-ready change is complete.
- Keep review read-only. Do not edit code, stage files, switch branches, stash changes, or create commits unless the user separately asks for fixes.
- GitHub metadata and checks apply only when a PR is actually in scope. For a local review, mark remote checks `not applicable`; never require the user to create a PR first.
- For a PR, GitHub check conclusions are the source of truth for remote CI. Local verification is complementary evidence and never substitutes for unread, pending, or failed remote checks.
- Separate the code-review verdict from delivery readiness. `Approve` accepts the reviewed code; it does not certify mergeability, QA, deployment, or release. Failed or pending delivery checks do not by themselves require `Request changes`. Honor a repository rule that explicitly makes a named check a prerequisite for code approval, and cite that rule rather than inferring one from a merge or release requirement.
- A review request authorizes a recommendation, not an external action. Do not approve, comment on, merge, rerun, or update a PR unless the user explicitly requests that separate action; submitting a verdict follows step 7.
- Verification must preserve user files and shared systems. Do not run fix/update modes, dependency installation, generators, migrations, deploys, snapshot updates, or tests that write shared databases/services without separate authorization or an isolated fixture.

## Review Round Limit

- A review round is one complete assessment of the same logical change after a distinct fix attempt. The initial assessment is round `1/7`; extra inspection, tests, or independent opinions on the same artifact stay in that round.
- Assign a cycle ID and stable change key before counting: repository + PR lineage + logical scope fingerprint for a PR; repository + logical request and target lineage for a commit/range; repository + request and scope fingerprint for a workspace review. Also retain repository + PR number as the PR container key so every included cycle remains visible. Carry these identifiers in review reports and agent handoffs.
- Before declaring `1/7`, search available task and review records for the same stable key and, in PR mode, for unresolved cycles under the same container key. A genuinely new target with no matching cycle starts at `1/7`; a matching cycle keeps its counter across commits, force-pushes, new tasks, agent handoffs, and renamed findings. If a matching cycle exists but its count cannot be recovered, require human confirmation instead of resetting it.
- Adding unrelated changes to an existing artifact or PR does not reset its unresolved cycle. A separately scoped target may receive its own cycle, but the combined deliverable cannot `PASS` while an older included cycle remains blocked or escalated.
- On rounds 1–6, return the evidence-backed decision and unresolved items. The next assessment increments the counter only after a new fix attempt is submitted.
- On round 7, `PASS` completes the review. If the result is `BLOCK` or `UNVERIFIED`, stop the automated review-fix loop, label the outcome `HUMAN_CONFIRMATION_REQUIRED`, and summarize unresolved findings, attempted remedies, evidence gaps, and the concrete decision needed. No review may be numbered `8/7`.
- Human confirmation chooses the next action: accept an explicitly stated `should_fix` risk, select a fix, narrow or stop the work, or authorize a new bounded cycle. A continued cycle requires a new cycle ID, starts at `1/7`, and retains the prior cycle's `7/7` escalation record. Before a new cycle starts, restate the **original intent** (step 2) and the current **scope drift** list; the new cycle covers that intent, and drifted units are reverted or split out rather than re-bounded into it.
- A finding or evidence gap carries across rounds until revision-bound new evidence or an explicit requirement change resolves it. Risk acceptance cannot erase a `must_fix` or missing evidence material to code correctness. A delivery gate remains blocked until it passes, but does not turn an otherwise passing code review into `BLOCK`. Human confirmation cannot convert code `UNVERIFIED` to `PASS` without resolving the material uncertainty.

## Review Modes

Choose exactly one mode from the user's request:

1. **Current workspace — default**
   - Use when the user asks to review “当前修改”, “本地改动”, “这些代码变更”, “review current changes”, or invokes this skill without another target.
   - Honor repository instructions or an existing review-scope resolver first.
   - Otherwise inspect `git status --short`, `git diff HEAD --stat`, `git diff --cached`, `git diff`, and `git diff HEAD`.
   - Unpushed commits are local changes too: list `git log --oneline @{upstream}..HEAD`. With no description of the change in the request, all of them are in scope and together form the requested change; when the request describes the change, commits outside that description are preserved exclusions, each named, and the verdict states that they are not covered and would ship unreviewed with a push. Diff committed work from `git merge-base @{upstream} HEAD`, never from the upstream tip, where a diverged upstream shows its own commits as reverse changes; when any unpushed commit is excluded, review the included ones commit by commit. Review `HEAD` → workspace as above, and state the commit count and the uncommitted file count separately. Without a usable upstream (none, gone, or a detached HEAD) there is no unambiguous base: say so, review the uncommitted changes, and offer HEAD's commits since its merge base with the integration branch the repository instructions name, if any, as a target instead of choosing it.
   - Open relevant untracked source, test, config, migration, and documentation files reported by status. Distinguish required files from unrelated user work.
   - Treat the workspace artifact (staged + unstaged + required untracked files) separately from the index artifact (staged content only). For files with both staged and unstaged edits, review both versions; unstaged or untracked corrections cannot prove the index artifact is commit-ready.

2. **Commit or range**
   - Use when the user supplies a commit, GitHub commit URL, tag, branch, or comparison range.
   - Record the literal diff expression, resolved object IDs, and merge base when the comparison uses one. Preserve the user's `A..B` versus `A...B` semantics; for a single commit, state its parent comparison, and for a branch without an unambiguous base, report the unresolved scope instead of silently choosing one.
   - Inspect author/message metadata, the commit list for a range, and the complete resolved diff. A commit URL remains commit mode; do not require PR-only merge or checks metadata unless a PR is explicitly in scope.
   - Do not silently replace the requested range with the working tree.

3. **Pull request**
   - Use when the user supplies a PR URL/number or explicitly requests PR approval.
   - Read repository/PR identity, title, author, base/head names and object IDs, merge base, commits, changed files, draft/review state, merge state, branch-protection status, and remote checks when GitHub access is available.
   - If the PR cannot merge, identify whether the cause is a conflict, stale branch, branch protection, missing review, failed or pending check, unresolved conversation, or another explicit gate.
   - Read unresolved review threads, each human reviewer's latest state, and review-bot findings on the current head. Treat their claims as candidates to verify against source. Record unresolved threads and outstanding `CHANGES_REQUESTED` separately; call them enforced merge gates only when platform/project rules make them so. A clean independent code review can coexist with another reviewer's unresolved opinion; do not clear that person's veto.
   - Keep local verification distinct from remote CI; neither substitutes for the other.

There is no change to review when nothing is uncommitted or unpushed and no target was named. Offer targets instead of choosing one: state the branch (or the detached SHA), its upstream (or, without one, HEAD's commits since the merge base with the integration branch the repository instructions name, if any), the branch's open PR, and the last commit's short SHA and subject, then wait. `HEAD~1..HEAD` is whatever landed last, often a merge or someone else's work, so it is never a silent default.

## Required Outcome

Answer these questions with evidence:

- What behavior is being added, fixed, or changed, and is it genuinely useful?
- Does the implementation satisfy that behavior on the real production path?
- Are correctness, security, data integrity, compatibility, and error handling acceptable?
- Is the complete change set present, including required tests, migrations, config, and documentation?
- Do relevant verification commands pass?
- For a PR, do remote checks and review/merge gates pass; if not, what exact gate blocks delivery?
- Should the current change proceed, or is it blocked?

Classify findings separately from the delivery decision:

- `must_fix`: blocks proceeding.
- `should_fix`: should be resolved before proceeding unless the user explicitly accepts the risk.
- `suggestion`: optional, non-blocking improvement.
- `accepted`: positive behavior supported by named evidence; it is not a substitute for missing verification.

Use exactly one **code-review verdict**:

- `PASS`: scope identity is stable, the reviewed patch is self-contained, every hotspot sweep is complete, there are no `must_fix` or unresolved `should_fix` findings, and verification needed to establish code correctness is satisfied.
- `BLOCK`: a confirmed blocking defect exists, the reviewed patch is incomplete, or a failed verification demonstrates a defect in the change. An explicit repository prerequisite for code approval can also block approval; name it separately from code defects.
- `UNVERIFIED`: the scope or revision changed, a required source artifact could not be read, evidence material to code correctness is missing, or a hotspot sweep has unchecked cells. The absence of a confirmed finding alone does not prove `PASS`.

In PR mode, report **delivery readiness** separately: `READY`, `BLOCKED`, `WAITING`, or `UNVERIFIED` (`NOT_APPLICABLE` for local-only review). List actual platform-required checks and explicit project merge/QA/release gates with their sources. Failed non-required CI remains visible as advisory evidence; do not invent a hard gate. If delivery facts alone are unavailable, retain the code verdict and mark delivery `UNVERIFIED`. `PASS + delivery BLOCKED/WAITING` is valid and can be approved when authorized, with the remaining conditions disclosed. If a check failure reveals a code defect or leaves material correctness uncertain, classify that evidence in the code verdict as well.

## Workflow

### 1. Resolve and freeze the scope

- Read applicable repository instructions before deciding the scope: the root instruction files plus every instruction file (`AGENTS.md`, `CLAUDE.md`, or the repository's equivalent) in a directory that contains a changed file or one of its ancestors. A rule binds a file only when its instruction file sits on that file's path.
- Record the review mode, exact diff expression, resolved object IDs, applicable merge base, changed-file list, and whether files are staged, unstaged, or untracked.
- In PR mode, also snapshot repository/PR identity, base/head object IDs, merge base, commit list, changed-file count, draft/review/merge state, and named remote checks so all evidence is tied to the observed head revision.
- In current-workspace mode, inspect the complete working state. `git diff HEAD` does not include untracked files, so reconcile it with `git status --short`.
- Exclude unrelated user files from detailed review and list them as preserved exclusions; report any unrelated tracked change mixed into the target diff. Any other exclusion (binary, generated, vendored, lockfile) also needs a stated reason; never drop a file silently.
- Resolve path-scoped review rules from repository instructions: match each changed file against the checks the repository defines for its path (for example migration paths → schema gates, service paths → that module's build). Record which rule applied to which files; a path with no rule is not a finding.
- Recheck scope identity before the final verdict. A changed patch/head invalidates affected code evidence until reviewed; return code `UNVERIFIED` if it cannot be refreshed. A check, review, PR-body metadata, or merge-state change on the same head requires refreshing delivery facts, not automatically discarding code evidence; reassess code only if the new facts affect its scope or correctness.

Completion condition: every file in the resolved scope is accounted for, and required untracked dependencies are identified.

### 2. Establish the changed behavior

- Fix the **original intent** first, then derive behavior from it (see “Original intent and scope drift” below).
- Review records, evidence documents, and pass claims shipped with the change are the author's claims. Read them for intent and verify only what the verdict relies on; they never narrow the sweep or set this review's round counter.
- Follow entry points through services, callers, persistence, external boundaries, and observable output.
- Map the **attack surface** the change reaches: for every changed production or configuration file, the user inputs (request parameters, headers, body, path and URL parts, deep links, uploaded files, device payloads), database queries, authentication and authorization checks, session and state operations, external calls (HTTP clients, webhooks, presigned URLs, queues, model providers), cryptography and secrets, and log or error output carrying user data that its added, changed, or removed lines touch or feed. Write `none` for a file whose lines reach none; tests and documents are `none` unless they configure production. A `required` unit with a non-empty surface is a hotspot under “Inputs and trust boundaries”.
- Rank **hotspots**: the `required` units the change touches that fall under a row of the hotspot sweep table in step 3, ordered by how much hidden damage a defect there could do. Give hotspots the deep pass before gate checks, evidence documents, locale files, and the remaining ledger. A `drift` unit gets a ledger pass that names what it changes; it is not swept as a hotspot of this change.
- For a bug fix, reproduce the original failure and show it passes with the change when feasible. If direct reproduction is impossible, use an equivalent control or mutation and record the remaining evidence gap; a test that also passes without the implementation is not proof.

#### Original intent and scope drift

- **Original intent** is the problem the change was opened to solve, taken from the earliest stable sources: the user's request, the linked task/issue/release id, the branch name, the first commit, and the PR title and description as first created (`gh api repos/<o>/<r>/issues/<n>/timeline`, the first commit, or the earliest edit). Record it in one sentence in the report and carry it unchanged across rounds and cycles.
- Later PR descriptions, commit messages, and contract or workflow documents added by the same change are the author's claims about the change; they can record drift, and they never widen the original intent.
- Classify every changed unit as `required` (the original intent cannot be met without it) or `drift` (anything else: opportunistic refactors, fixes for unrelated failing checks, new behavior in other features). Name the dependency that makes a unit `required`.
- Report `drift` as one `must_fix` titled “scope drift”, listing the drifted units with the commit that introduced each; its fix direction is to revert them from this change or split them into a separate change with its own review. Defects found inside drifted code go into that finding as evidence and into a separate task list; they are not fix requests against this change, because fixing them grows the drift.
- A drifted unit becomes in scope only when the user (not the author) explicitly widens the original intent in the current conversation or task record; record that authorization in the report.

Completion condition: the report states the original intent with its source, every changed unit is `required` or `drift`, the report can state the old behavior, new behavior, and production path that connects them, every changed file has its attack surface listed or `none`, and the hotspots are ranked.

### 3. Inspect every change

- Review all changed production, test, migration, config, and documentation files.
- Keep a per-file ledger keyed by `(path, status)` — the same path can appear twice when a staged deletion is followed by an untracked recreation. Every in-scope file ends `reviewed` or `skipped` with a concrete reason. Do not stop after the first blocking finding, and do not skip a file because it is small or secondary to its group (header, interface, config, test, locale variant).
- A read whose output was truncated (`…tokens truncated…`) covers only the lines it showed. Re-read the missing range in smaller chunks before marking the file `reviewed`.
- Review related files as one unit: interface and implementation, producer and consumer, DTO/mapper/migration, and locale or config variants of the same resource. Check the unit for inconsistent updates, missing counterpart changes, and broken contracts. For a large diff, work through such units in bounded batches.
- Check behavioral regressions, trust boundaries, authorization, data consistency, concurrency, transactions, null/error paths, N+1 or other data-access regressions, performance, API compatibility, and configuration drift as applicable.
- Read the `-` side of every hunk; the post-change code cannot show what is gone. A removed guard (validation, authorization or ownership check, null check, rate limit, feature flag), constraint or index, lock or transaction boundary, cleanup (`finally`, dispose, cancel, unsubscribe), timeout or retry, audit or log call, translation key, accessibility attribute, test or assertion, or security setting is a lead. Settle it by its replacement in the change (moved, renamed, or centralized in a shared guard), by an unchanged guard that already covers every path, by the removal of what it guarded in the same change (the resource, caller, or surface; cite that hunk), by the original intent asking for the removal (cite it), or by showing the removed code was already unreachable at the base; with none of these, it is a **regression**. Count leads by removed behavior, not by line.
- Run the hotspot sweep below on every hotspot.
- Treat each finding as one instance of a **defect class**, named by its mechanism rather than its symptom: a check present on one handler but missing on its siblings, a field mapped by one serializer but not another, a cache left stale by one write path, state written from an outdated snapshot, an error swallowed in one branch. Before reporting, sweep the whole scope for **siblings**: the same helper or field, sibling operations in the same unit, parallel implementations in other files. Report confirmed siblings with the finding.
- Within `required` units, flag **overbuilding**: code, configuration, abstraction, guard, compatibility path, or test the original intent does not need — a speculative option, a wrapper or interface with one caller, a guard for a state no caller reaches, a test pinning incidental output. Name the intent-level need it lacks and give delete or narrow as the fix direction. Grade it by weight: `should_fix` when it changes runtime behavior, adds a public surface (endpoint, parameter, config key, schema, dependency), or adds a module or layer of its own; `suggestion` when it is a few inert lines — an unreachable early return, an unused type member or field, a redundant comment or test case. Validation at trust boundaries, data-loss prevention, security, and accessibility basics are never overbuilding. Code, guards, and tests added to resolve an earlier finding of this cycle are needed to the extent that finding requires them; flag only what exceeds it, and when the earlier fix direction itself asked for the addition, correct that direction in the report instead of charging the author. A whole unit outside the intent is scope drift, not overbuilding.
- Verify tests assert externally meaningful behavior and cannot pass for the wrong reason. Map each new branch, error path, boundary, and negative validation case to a test or another named piece of evidence, and grade an uncovered one by what its failure would break: data loss, a security hole, or a user-visible error is a finding; a trivial accessor is omitted.
- Give every finding a **cause** by what produced it, not where it surfaces: `introduced` (the change created it, made a dormant defect reachable or an existing one worse, or left in place a defect the original intent asked it to fix: an incomplete change), `regression` (the change removed or weakened behavior that was correct at the base and that the original intent did not ask to change, including through an untouched consumer of a changed contract, token, or default), or `pre-existing` (present at the base, not made reachable or worse by the change, and not a defect the original intent asked it to fix). Decide it from the pinned diff and the mechanism; blame only dates a line: `git blame <base>..<head> -- <path>` (with `--contents <path>` for uncommitted edits) attributes lines older than the change to the boundary commit, shown as `^` or, under `blame.blankBoundary`, a blank hash, and an untracked file is new in full. A defect inside deleted code is gone with it; the deletion itself is judged by the `-` side rule above. A `pre-existing` finding is a `suggestion` whose fix belongs to a separate task: report it in its own section, at most three, most damaging first, with the count of the rest. A contract, workflow document, or test added by the same change does not make it this change's responsibility.
- Leave out style nits and merely redundant comments unless a repository rule requires them; a `suggestion` must be worth the reader's time. A changed comment, docstring, or document that misstates the code (wrong parameter, return value, or edge case; a reference to renamed code; a TODO the change already resolved) is a correctness finding.
- Report a repository-rule violation only with the exact rule quoted, its instruction file named, and that file's scope shown to cover the changed path. An explicit in-code suppression (lint-ignore, documented exception) is a deliberate decision: check that it is narrow and justified rather than re-flagging the suppressed rule.
- Cite exact files and line numbers for findings.

Completion condition: the ledger accounts for every in-scope file, the `-` side of every hunk has been read, every hotspot sweep has no unchecked cells, every finding has a cause and its class has been swept for siblings, and every changed line has a defensible relationship to the requested functionality or is reported as scope drift.

#### Hotspot sweep

Following one path finds the first defect; a sweep finds its neighbours. One confirmed defect opens the sweep; it never completes it. For each hotspot:

1. Write the hotspot's **invariants** first: the properties every path must keep (for example “every accepted stop ends in a cancel or a terminal state”, “every waiting state exits on every terminal outcome”, “a cancel targets the request currently observed”). Sweep against the invariants, not against the paths the change author fixed.
2. Take every row below that applies and enumerate its cells from the code itself: the operations, inputs, callers, suspension points, and outcome classes it actually has. Group cells that one guard settles, and name the guard.
3. Mark every cell `ok`, `defect`, or `unreachable`, citing lines. An unchecked cell is an evidence gap.
4. When a hotspot's interleavings exceed what reading settles (roughly more than 20 cells after grouping, or any cell whose answer depends on the order of two async completions), read [`references/interleaving-model.md`](references/interleaving-model.md) and follow it: write the execution model, reduce it to **legal orders** (causality, commutation, critical placement before/after each relevant suspension point, one representative per guard and outcome class), and drive every reduced order with an **interleaving harness** that runs the real module under a controllable scheduler or deferred promises. Under a read-only sandbox, run the harness in memory (`node -e`, stdin, or `--eval`) instead of writing a file, and quote the order list and results in the report. If the harness cannot run, walk each order by reading with cited lines; orders neither driven nor walked stay unchecked.

The sweep is a **matrix**, written out in the report: per hotspot, the invariants, the rows applied, cells total / `ok` / `defect` / `unreachable` / unchecked, and how each was checked (reading, harness, test); for a modelled hotspot, also the reduction chain from raw to reduced orders. A hotspot reported only in prose counts as unswept, and the decision is `UNVERIFIED`.

| Hotspot | Cells to enumerate | Check in every cell |
| --- | --- | --- |
| Shared state written by async work | each pair of operations writing one field, including two runs of one operation × every start/finish order × each outcome class (success, explicit rejection, retryable failure, unknown acceptance, not cancellable yet, terminal, superseded) | writes start from current state, not a start-time snapshot; every copy or rebuild helper carries every field; a retired operation's flags get cleared; a late completion stays safe on the state that replaced its own; merges keep the newest data; one item's failure in a batch survives later successes |
| Entry points and wiring | every caller, route, menu, deep link, and legacy path reaching the changed behavior × every new parameter, callback, flag, or config key | each path receives the new wiring; legacy paths route through the new behavior or are removed; each action touches only its intended target |
| Inputs and trust boundaries | each attack-surface item (step 2) × valid, empty, boundary, malformed, oversized, and hostile values × caller identity and tenant | validation and authorization hold on every path, including retries and batch variants; every class in [`references/security-checklist.md`](references/security-checklist.md) that can reach the item is settled by a named guard or reported |
| Persistence and contracts | each write path (create, update, delete, retry, migration, backfill) × concurrent writers × old and new readers | constraints and transactions hold; existing data and older clients still work; producer and consumer agree on names, types, nullability, and envelopes |
| Failure and recovery | each failure branch (network, 4xx, 5xx, timeout, cancellation, partial success) × each handler that meets it: catch block, error callback, default or fallback value, optional chaining or null coalescing that skips work, retry loop | the user-visible state is right; a retry exists, is idempotent, and reports exhaustion; a catch takes only the error types it expects (name the unrelated errors a broad one would hide); the log names the operation and identifiers; a fallback is specified behavior, never a silent default or a mock/stub outside tests |
| Lifecycle and resources | create, dispose, cancel, background, scope or account switch × in-flight work | in-flight results land on the right owner or are dropped; listeners, timers, and subscriptions are released |
| Instances sharing persisted state | each pair of instances that read or write one shared record (tabs, windows, processes, devices, workers) × every suspension point (`await`, callback, timer) in each instance's protocol × every foreign write the other instance can make there (claim, replace, update, clear, terminal, takeover) | each instance re-reads the shared record after every suspension instead of trusting local refs captured before it; a user intent (stop, cancel, delete) recorded by one instance is carried out by whichever instance owns the work, or the recorder carries it out itself; every instance waiting on the work leaves its waiting state on every terminal or foreign clear; local caches of another instance's identifiers are invalidated when the record changes owner |
| Types and invariants | each new or changed type, state model, or enum × every constructor, deserializer, mutation path, and external writer | invariants hold at construction and after every mutation, not only through documentation or caller discipline; illegal combinations are unrepresentable where the language allows, otherwise rejected at the boundary |
| New variants and states | each variant the change adds (enum value, status, mode, flag, setting, endpoint, user-facing string, theme or size) × every place its existing peers are handled, found by searching for the peers rather than reading the diff: `switch`/`when` arms, mappers and serializers, validation lists, client models in other repositories, each supported locale's catalogue, UI states (loading, empty, error, disabled, focus, narrow width, dark mode), sibling surfaces that carry the peers | the variant reaches every place its peers do, directly or through inheritance, or the code or the original intent says why not; an **incomplete change** shows only as an absence, which no diff contains |

#### Round 2 and later

- Before the sweep, classify the new fix commits against the original intent. A fix commit that touches units outside the original intent extends the drift finding; the recommendation is to revert or split, and the drifted units get no new fix requests in this cycle.
- When the same hotspot has produced findings in two or more rounds and lies outside the original intent, the recommendation is to split it out, not another fix round.
- The target is the whole current revision. A caller's focus (for example “重点确认 X 是否修复”) orders the work; it does not narrow it. Verify the fix, then rerun every hotspot sweep on the current revision, including cells the fix did not touch.
- Record `git diff --shortstat <base>` for the current revision next to the previous round's figure (round 1 records the baseline). Growth that neither the original intent nor the fixes for earlier findings of this cycle explain is evidence for the scope drift or overbuilding finding; name the units that grew.
- For each new finding, check whether its cited lines already existed in an earlier reviewed revision (`git log -L`, `git blame`, or `git diff <earlier-head> -- <path>`). Label it `introduced-by-fix (<sha>)`, `missed-earlier (present since <sha>)`, or `pending-confirmed` when an earlier round's pending candidate is now confirmed by new evidence. A `missed-earlier` finding means its class was under-swept: name the matrix row and the cell that should have caught it, record the entry point, state, or assumption the earlier round missed (write `unknown` when it genuinely is; never invent a reason), add the missing cells to that hotspot's matrix (or add the missing row), and rerun the whole matrix for that hotspot across the scope before reporting. Then check every path with the same mechanism for the same omission. A `pre-existing` finding records its origin only; the re-sweep is for defects this change caused.
- When earlier rounds already reported a finding in a hotspot, treat that hotspot as one where reading has failed: follow the interleaving model for it even if the cell count is below the threshold.

### 4. Verify impact and completeness

- Identify affected modules, endpoints, schemas, callers, consumers, jobs, and deployment/runtime configuration. The impact scope is the diff plus its unchanged direct neighbours: every caller, consumer, data store, and external interface the changed code reaches. Record them in the report as a short adjacency list (`changed unit → unchanged neighbour → what was checked there`); a neighbour named only as "callers" is unchecked.
- A shared primitive (design token, theme value, shared component or hook, common library or starter, base class, global default) has a **blast radius** past its direct neighbours: expand to the second hop, reading each consumer at the revision the change ships with (another repository's companion head or target branch, never a local checkout of unknown state). Group consumers that one guard settles and count by group; consumers no group covers are an evidence gap with their count stated, because an unstated cutoff reads as completeness.
- Check whether related tests and documentation need updates.
- Confirm referenced new files are included in the reviewable change set.
- For local changes intended to be committed, distinguish “current workspace passes” from “the exact tracked patch is self-contained.” If unrelated tracked changes would ship with the same patch, a bounded functional review is not a commit-ready `PASS`.
- Verify a commit, range, or PR against its exact resolved revision in an isolated directory that does not change the source repository's branch, index, worktree metadata, or user files. For a range, test the resolved right endpoint while keeping diff scope anchored to the user's operator (`A` for `A..B`, merge base for `A...B`). If exact-artifact verification is unavailable and materially required, return `UNVERIFIED`.

Completion condition: downstream impact and change-set completeness are supported by direct evidence.

### 5. Run proportionate verification

- Derive required checks from repository instructions, affected package scripts, CI configuration, and changed file types; label any additional checks optional.
- Run the narrowest behavioral test that proves the changed functionality first, then the affected module's required full test/build command.
- For uncommitted workspace changes, test in place when isolation would omit required local state; keep the repository read-only and report workspace evidence separately from patch-self-containment evidence.
- Inspect command side effects before execution. Avoid fix/update flags and redirect caches, coverage, and build output to an isolated location when the repository supports it; do not disrupt an active runtime to obtain review evidence.
- Record each command's working directory, exact revision/artifact, exit code, pass/fail/skip counts, evidence level (`static`, `unit/mock`, `integration`, `real runtime`, or `remote CI`), and concrete blocker. Mock-only evidence cannot establish real-runtime behavior.
- Recheck repository state after verification. If a command unexpectedly changes tracked or user-visible files, do not clean or restore them; report the side effect and return `UNVERIFIED` until the evidence can be reproduced safely.
- In PR mode, read the remote checks against the **actual required set**: base-branch rulesets (`gh api repos/<o>/<r>/rules/branches/<base>`) and classic branch protection (`gh api repos/<o>/<r>/branches/<base>/protection/required_status_checks`; a 404 on that endpoint means no classic required checks, not that rulesets are absent). If neither configures required checks, record `platform required checks: none`; do not promote all CI to required. Separately list explicit project gates and whether they govern code approval, merge, QA, or release, quoting their source. Other checks are advisory to delivery, but their evidence can still reveal a code defect. A required check not started is pending, never green by omission. For repeated runs use the newest attempt of the same trusted check identity and triggering event; do not let another App/creator's success erase a failure. Report failed, pending, skipped, unavailable, and advisory states precisely; local commands cannot establish remote success.
- When the base branch moved after the head's last green run, compare the new base commits with the PR's files (`gh api repos/<o>/<r>/compare/<old-base>...<new-base>`). Overlapping files make the gate `stale` even when GitHub reports the PR mergeable; name the overlapping files.
- For each failed check, decide whether the change causes it: compare its area with the diff and inspect base/recent-run evidence. A pre-existing or flaky failure blocks delivery only if it belongs to an actual required check or explicit project gate; it does not alone block code approval. A regression demonstrated by an advisory check still blocks the code verdict. Recommend a rerun or separate tracking where appropriate; do not rerun without authorization or repair unrelated code to make this PR green.
- Diagnose opaque flow errors with the checker/policy revision pinned by that run and current PR metadata. A generic code such as `OTHER_BLOCKED` does not establish that an outstanding review caused the failure. Verify task-link syntax and accepted resource types against that checker; do not assume the link must be an Issue when commits or other task records are accepted.
- Do not claim remote checks passed unless a PR exists and those checks were read. Do not let green remote CI override a code-level `must_fix` or an incomplete change set.

Completion condition: each correctness claim names fresh verification evidence or an explicit verification gap; code-approval prerequisites and delivery gates have named sources and separate outcomes.

#### Evidence scaled to risk

Keep the default review lean. Add an artifact only when it proves a named claim or materially reduces reviewer effort:

- For a bug fix, confirmed finding, or non-obvious manual flow, give minimal reproduction steps or exact triggering preconditions. Provide copy-paste reviewer verification steps with the expected result only when the verification log is not already sufficient; do not duplicate it.
- If TDD is claimed or required, tie a failing baseline run and passing changed-revision run to their commands and revisions. A green test on the current code proves behavior, not the historical red-green sequence; missing TDD provenance makes the TDD claim unverified, not automatically the code itself.
- For user-visible UI, media, or interaction changes, inspect the surface at the reviewed revision when needed to establish correctness or required by the project. Valid evidence is a fresh reviewer capture, a same-head UI CI job exercising the changed surface, or a head-bound author capture spot-checked against the code. Older/unbound captures remain claims. Record missing runtime/UI evidence with its consequence: if correctness cannot be established without it, code is `UNVERIFIED`; if it is a remaining QA/release acceptance step and code correctness is otherwise supported, retain the code verdict and disclose it under delivery. Never claim the surface or real media was verified from mock tests alone. Report defects seen while capturing; keep own captures outside the worktree and do not upload without authorization.
- For a large or cross-cutting diff, provide a compact change map or use an available diff-visualization capability when raw patches obscure the behavior. Use Mermaid only when relationships among at least three components or an event ordering are materially clearer as a diagram. A change diagram says what the system did before, what it does now, and which unchanged neighbours are affected; it binds every node to the reviewed revision (path and line range) and is checked against that code before it is used. Draw it after the independent reviewers have reported, never as input to them, so it cannot pre-shape their reading; a diagram that needs a paragraph of explanation is a sign the change map is wrong, not that more prose is needed.
- For durable architecture, public API/schema, security-boundary, or migration decisions, compare the implementation with an existing design document or ADR. Treat a missing document as blocking only when repository policy requires it or the decision cannot be reviewed safely without it; otherwise classify the documentation need proportionately.

#### Independent review panel

- Trigger: run a panel when the change involves security boundaries, irreversible data, public contracts, concurrency/lifecycle behavior, or coordinated services, when a prior round reported a finding, when the verdict would be a consolidated recheck (below), or when the user asks for one. Otherwise the primary review stands alone and records `panel: none`.
- Size: **quick** = 2 reviewers (default when triggered); **full** = 6 reviewers only when the user asks for a full review (“完整评审”, “full review”). Never more than six, never fan out to every available agent, never fewer than the panel size.
- Every reviewer reads the whole change at the same fixed revision and may report anything; angle ownership sets depth, not scope. The six angles and their owners:

| Angle | Quick (2) | Full (6) |
| --- | --- | --- |
| Requirements and business correctness | A | 1 |
| Errors and recovery | B | 2 |
| Concurrency and lifecycle | B | 3 |
| Security and data integrity | A | 4 |
| Call chain and regression impact | A | 5 |
| Test validity and refutation | B | 6 |

- Within its angle each reviewer takes the top-ranked hotspot not yet fully swept; a quick panel reduces depth of enumeration, never a risk category. An angle that does not apply to the change is marked not applicable with the reason, by the owning reviewer and in the record.
- Independence: a reviewer receives the scope, the revision, its angles, its hotspot, and the original intent with the `required`/`drift` classification; not the primary's conclusions, not other reviewers' reports, not prior review comments. Describe intended behavior from the original intent; author-written contracts are passed as claims to verify, not as requirements. A reviewer for whom that did not hold is not a panel reviewer: leave it out of the record and replace it.
- Each reviewer reports three lists, each item with a stable id and a location: **confirmed** (trigger condition, impact, evidence), **pending** (what is suspected, what evidence is missing, how to verify), **rejected** (a candidate it had concrete grounds for, and the code that refutes it). No padding: a guess without grounds is not a candidate. A pending item is never dropped for not having been reproduced yet.
- The primary adjudicates every candidate in a ledger (`references/review-record.md`): each reviewer's original three lists are kept as `reviewer_reports`; merged duplicates keep every source and source item; each candidate ends `confirmed` (severity, cause, and evidence), `rejected` (the refuting code), or `pending` (missing evidence and whether it blocks `PASS`). A confirmed `should_fix` blocks `PASS` unless the user's explicit risk acceptance is recorded on it (`accepted_risk`); a `must_fix` can never be risk-accepted. A finding carried over unresolved from an earlier round is `carried-over` with its first round, not a new finding. Opinions merge by evidence, not by vote. The primary also sweeps for gaps outside the candidate list (hotspots no reviewer reached, angles with thin evidence) and records them as `coverage_gaps`.
- Write the record outside the reviewed worktree, with `primary.skill_version` set to this skill's `metadata.version`, and run `scripts/check_review_record.py <record>`; under a read-only sandbox where no path is writable, pipe the JSON to `check_review_record.py -` instead and include the full record in the report. The report's counts are derived from the record. A failing check is an evidence gap: fix the record if it misdescribes the review, never delete a candidate or a gap to make it pass, and do not issue `PASS` on a failing record. The checker proves record consistency only; it does not replace headcount, independence, or rounds.
- Counting: all panel opinions on one revision are one round; rounds advance only on a new fix attempt; six clean reports are not six rounds and do not shorten the round rules.
- If the reviewer producing the verdict authored or edited any part of the change under review, the verdict is a **consolidated recheck**, not an independent review: say so in the report and in the record (`verdict_kind`), and run at least a quick panel whatever the verdict.

Completion condition: every included artifact supports a named behavior, risk, or decision. Optional artifacts whose trigger did not apply are omitted and are not evidence gaps.

### 6. Produce the verdict

- Recheck every finding against the reviewed revision before reporting. Reopen the cited file at the cited lines and confirm the quoted code is there; correct drifted line numbers (new-file coordinates).
- Then try to refute each finding as a reviewer who believes the code is correct: look for the upstream guard, another hunk of the change that already handles it, the definition or override elsewhere, the caller that makes the path unreachable, an existing test that exercises the exact scenario, the instruction file's scope, and any in-code suppression. A compiler, type-check, or lint failure already in the verification log is reported once, as that failed command.
- Remove a finding only when the code proves it wrong. A plausible finding that could not be confirmed is not dropped silently: it cannot be `must_fix`; report it as `should_fix` with the open question, or as an evidence gap when it is material to the decision.
- Put the conclusion first.
- Apply the code-verdict and delivery-readiness rules from Required Outcome independently; do not convert a delivery-only failure into a code finding.
- Before recommending a fix for a `suggestion` (or an item you are unsure is worth changing), triage it with [`references/suggestion-triage.md`](references/suggestion-triage.md); report a `SKIP` as “not worth fixing” with the three probabilities. Never use it on `must_fix`, `should_fix`, or a `pre-existing` finding, whose fix is a separate task.
- Order findings by `must_fix`, `should_fix`, then `suggestion`, security findings first within each; omit empty detail where brevity helps, but explicitly say when no blocking finding exists.
- Explain why each finding matters, when it occurs, and what outcome it can cause, then give the fix direction. State each finding's cause; a `regression` quotes the removed or weakened line beside whatever replaced it. Include a code snippet only when applying it alone resolves the finding; describe a fix that spans several locations or needs follow-up steps in prose. For a defect inside drifted code, the fix direction is revert or split (see “Original intent and scope drift”).
- Report each hotspot's sweep in one line: rows applied, cells checked, defects, unreachable.
- When one piece of evidence rules out the most charitable reading of the change — a test proving the behavior was intended, a comment showing the tradeoff was already accepted, a caller proving the path is hot — name it and state what it rules out. Never manufacture significance for a routine finding.
- Separate implementation quality, impact scope, local verification, and remote checks.
- In PR mode, include the exact merge-gate state and distinguish “code accepted / can approve” from “ready to merge/release”. Code approval must not be described as QA or release authorization.
- End with the code recommendation (`PASS / 建议代码评审通过`, `BLOCK / 代码评审不通过`, or `UNVERIFIED / 代码证据不足，暂不审批`) and a separate delivery status. A `PASS` can say “可 Approve；合并/发布仍待 …”.

### 7. Submit to the PR (explicit request only)

Run this step only when the user explicitly asks to submit the verdict to the PR (for example “审完直接 approve”, “提交 review”). Otherwise stop at step 6.

- Before submitting, refresh the PR head/base, open/merged state, current checks, latest reviewer states, and rules governing the action. If already merged/closed, report the outcome rather than posting an obsolete approval. If the head changed or cannot be read, do not submit a verdict for that unknown/unreviewed revision. On the same head, refresh check/review/body facts and revise delivery status; do not reuse an older failure after a trusted newer attempt passed. Re-read the head immediately before the write and bind the review to the full reviewed SHA in its body (and `commit_id` when the API supports it).
- Map the **code verdict** when the submission is authorized: `PASS` → `gh pr review <N> --repo <OWNER/REPO> --approve`, disclosing any delivery blockers; `BLOCK` → `--request-changes` for the code defect or explicit unmet code-approval prerequisite; `UNVERIFIED` → submit a non-approving `--comment` if a review verdict was requested, naming the material uncertainty. If authorization covers only approval on success, return non-passing findings without another external write. Never use `Request changes` solely to hold a PR for merge checks, deployment, or QA paperwork. Respect another reviewer's veto; do not dismiss it, bypass checks, merge, or enable auto-merge without separate authority.
- If the authenticated `gh` user is the PR author, GitHub rejects approve and request-changes; post the report with `gh pr comment` instead and say so.
- Pass the report with `--body-file`. Rewrite local absolute or worktree paths (for example `/tmp/prN/path:line`) to repository-relative `path:line`, and link each finding as `https://github.com/<OWNER>/<REPO>/blob/<full reviewed head SHA>/<path>#L<start>-L<end>` with one line of context on each side; a branch name or short SHA lets the link drift or break.
- If the review runs in a sandbox that cannot reach GitHub, return the final report and the mapped action; the caller submits it under the same rules.
- Report the PR, the reviewed head object ID, and the action submitted.

## Output Shape

Use the user's language; default to Chinese for Chinese requests. Keep the result concise and evidence-backed.

In a Chinese report, describe test names, check names, and assertion labels in Chinese by the behavior they assert; do not paste the English name, not even in parentheses after the Chinese. Cite the test file path when the reader needs to locate it. File paths, symbols, commands, and verbatim logs (exit codes, assertion diffs, stack traces) stay as they are.

```text
代码评审：PASS / BLOCK / UNVERIFIED — 可 Approve / 不通过 / 代码证据不足
交付状态：READY / BLOCKED / WAITING / UNVERIFIED / NOT_APPLICABLE — 具体条件及来源

审核轮次：
- Cycle ID / stable change key / PR container key when applicable: ...
- Review round: n/7
- Escalation: not required / HUMAN_CONFIRMATION_REQUIRED

范围身份：
- 原始意图（来源）: ...
- 模式与精确 diff: ...
- Resolved revision / PR base-head: ...
- 文件数与 staged/unstaged/untracked；未推送提交 n（纳入 n / 排除 n）: ...
- diff 规模: <shortstat>（第 2 轮起附上一轮数字与增长单元）
- 覆盖: reviewed n / skipped n（逐个原因）/ excluded n（逐个原因）
- 范围漂移: 无 / 单元 -> 引入提交 -> 处置（回退 / 拆分）
- 命中的路径规则: 无 / 规则 -> 文件

评审结果：
- must_fix: 无
- should_fix: 无
- suggestion: ...（既有问题单列在下方，不重复计入）
- accepted: ...
- 既有问题（pre-existing，不阻断）: 无 / 最多 3 条，最严重在前，另有 n 条
- 每条发现标成因：introduced / regression（引用被删或被削弱的原行及其替代）/ pre-existing
- 新发现来源（第 2 轮起）: introduced-by-fix (<sha>) / missed-earlier（自 <sha> 起存在）

热点扫描：
- 单元 -> 不变量 -> 适用行 / 检查格 n（ok n / defect n / unreachable n / 未查 n）/ 检查方式（阅读 n / harness n / 测试 n）；无热点时写“无”；只写文字描述视为未扫描

攻击面与安全检查：
- 文件 -> 攻击面（输入 / 查询 / 鉴权 / 会话与状态 / 外部调用 / 加密与密钥 / 日志与错误输出）；无则写“无”
- 安全类别 -> clean（守卫与位置）/ finding（发现编号）/ n/a（原因）；逐类列出，漏列类别视为未扫描；required 单元无攻击面时写“无攻击面”

关键证据：
- 行为或风险 -> 生产路径 -> 证据等级与结果

验证结果：
- 命令 | cwd | revision/artifact | exit | passed/failed/skipped | evidence level
- Remote checks: 平台 required 集合及来源 / 项目明确 gate（审批/合并/QA/发布）/ advisory；各项通过/失败/等待/未启动/无法读取
- PR 评审线程与 bot: not applicable / 未解决 thread n、CHANGES_REQUESTED 评审人、bot 发现 -> 裁决（confirmed / rejected / pending）
- Merge gate: not applicable / ready / conflict / stale（base 重叠文件）/ protection / missing review / unresolved conversation / pending checks / other

证据缺口：
- 无 / ...

影响邻接：
- 改动单元 -> 未改邻接（调用方 / 消费方 / 存储 / 外部接口）-> 检查内容；共享基础件另列第二跳与未覆盖消费方数量；无则写“无邻接”

独立评审（触发时）：
- panel: none / quick / full；verdict_kind: independent / consolidated-recheck
- 评审员 -> 角度 -> hotspot -> 独立结论（confirmed n / pending n / rejected n）
- 裁决清单：C<n> -> 来源 -> confirmed(severity, cause) / rejected(反证) / pending(缺什么，是否阻断)
- coverage_gaps；record 路径与 check_review_record.py 结果

按需证据（仅列命中触发条件的项目）：
- 复现与 reviewer 复验步骤 / TDD red-green 日志 / UI 观察（自截 / 同head UI CI / 作者截图+head；缺失影响代码正确性则代码 UNVERIFIED，否则列交付条件）/ 变更图 / design doc 或 ADR

最终判断：
修改是否真实有用：是/否
代码质量是否通过：是/否
影响范围是否可接受：是/否
是否建议当前修改通过：是/否
代码是否可 Approve：是/否及依据
合并/发布是否就绪：独立状态及未满足条件；不将代码批准当 QA/发布通过
判定规则：代码 PASS / BLOCK / UNVERIFIED 与交付状态各自的触发条件
```

## Common Issues

### The working tree passes but the patch does not compile

**Cause:** Required files are untracked or excluded from the selected diff.

**Action:** Report a `must_fix`, identify the missing files, and distinguish workspace verification from exact-patch verification.

### No PR or remote checks exist

**Cause:** The user requested a local code review.

**Action:** Continue the review from local changes and report remote checks as `not applicable`.

### The repository contains unrelated user changes

**Cause:** The working tree has multiple concurrent tasks.

**Action:** Preserve them, review only the resolved functional scope, and flag unrelated tracked changes that would ship with it.

### Verification cannot run

**Cause:** Missing service, credential, dependency, device, or environment capability.

**Action:** Record the failed command and missing evidence. If material to code correctness, code is `UNVERIFIED`; if only a QA/release acceptance step, retain the supported code verdict and mark delivery accordingly. Do not turn inspection into a runtime pass claim.

Under a read-only sandbox, toolchains that write caches or temp files (Flutter, Xcode, Gradle, some package managers) fail before any test starts, for example `couldn't create cache file '/tmp/xcrun_db-…' (errno=Operation not permitted)`. Record that blocker once and continue statically; static review then carries the full burden, and every hotspot sweep stays required.

### Local verification passes but the PR is still blocked

**Cause:** A remote check is failed or pending, the branch is stale or conflicting, branch protection is unsatisfied, or a required review is missing.

**Action:** Report the supported code verdict separately from the sourced delivery gate. `PASS` may be approved when authorized even while merge-required CI is pending/failed, unless an explicit repository code-approval prerequisite applies. Never claim merge/QA/release readiness or bypass the gate.

### GitHub checks are green but the code has a blocking defect

**Cause:** CI does not cover the failing production path, boundary condition, or incomplete change set found during review.

**Action:** Report the code defect as `must_fix`. Green CI is evidence, not permission to override a blocking finding.

### The evidence package becomes ceremonial

**Cause:** Diagrams, videos, design documents, or multiple agent reviews are added without proving a material claim.

**Action:** Remove redundant artifacts. Keep the verification log and add only the smallest conditional evidence that makes behavior, risk, or reproduction easier to verify.

### TDD is claimed but only a passing current test is available

**Cause:** The evidence proves the current behavior but not that the test failed before the implementation.

**Action:** Mark the TDD claim unverified unless a revision-bound red-green run or equivalent control exists. Judge code readiness separately from that process claim.

### A re-review arrives without a round counter

**Cause:** A handoff or prior review report omitted the iteration state.

**Action:** Resolve the stable change key and recover the counter from the same change's task history, review reports, or artifact lineage. If a matching cycle exists but the count remains unknown, request human confirmation; never reset it to `1/7` merely because the request or agent does not mention prior rounds.

### Each round finds one more defect that was already there

**Cause:** Earlier rounds stopped at the first confirmed instance of a defect class, or the re-review checked only the fix.

**Action:** Follow “Round 2 and later” in step 3: label the finding `missed-earlier`, rerun every hotspot sweep and the class's sibling sweep across the whole scope, and report every confirmed sibling in this round. A `pre-existing` finding records its origin only.

## Examples

### Current workspace

User says: “调用 local-review，review 一下我当前对登录功能的修改，不用提 PR。”

Result: review staged, unstaged, and relevant untracked files plus unpushed commits of the login change; trace the login path; run relevant tests; remote checks are `not applicable`.

### Commit

User says: “review commit abc123，看看这个修复能不能合并。”

Result: review exactly `abc123`, verify affected behavior, and give a pass/block recommendation without requiring a PR.

### Pull request

User says: “评审 PR #42，CI 绿了能不能 approve？”

Result: inspect the PR diff and metadata, independently review the code, run local checks where feasible, and report both local and remote results.

### Pull request with scope drift

User says: “复审 PR #57”，the PR was opened to add a missing file to a Docker build; later commits rewrote a feature's runtime state handling to get an unrelated flaky E2E check green.

Result: original intent = the Docker build input. The build change is reviewed in depth; the runtime rewrite is one `must_fix` “scope drift” whose fix direction is to revert or split it, and defects found there go to a separate task. The flaky check's remedy is a rerun plus a tracking task.

## When NOT to Use

- Do not use for implementing requested fixes; review first, then use the appropriate implementation workflow if the user asks for changes.
- Do not use for a general architecture explanation with no code change to assess.
- Do not use for monitoring CI after the review is finished unless the user explicitly asks to wait or monitor.
