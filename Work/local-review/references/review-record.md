# Review record

One JSON file per review of one revision, written outside the reviewed worktree (for example `$TMPDIR/local-review/<cycle_id>-<round>.json`). It is the ledger behind the panel section of the report; the report's counts are derived from it, never typed separately. `scripts/check_review_record.py <file>` checks the record for missing items and contradictions and exits non-zero on any; a failing record cannot back a `PASS`.

The checker proves the record is consistent with itself. It does not prove anyone read the code; headcount, independence, and rounds remain rules on the reviewers.

## Shape

```json
{
  "cycle_id": "example-org/shop#42/checkout-retry",
  "round": 2,
  "revision": "afaaa2a0116327b2c74fd9a54be5ab258c4ffb57",
  "panel": "quick",
  "verdict": "BLOCK",
  "verdict_kind": "independent",
  "delivery": {
    "status": "WAITING",
    "blockers": ["platform-required unit CI pending on this head"],
    "advisories": ["release QA has not been performed"]
  },
  "primary": { "executor": "codex gpt-5.5", "skill_version": "3.15.0" },
  "reviewers": [
    {
      "id": "A",
      "executor": "codex gpt-5.5 spawn_agent",
      "revision": "afaaa2a0116327b2c74fd9a54be5ab258c4ffb57",
      "angles": ["requirements", "security", "callers"],
      "hotspot": "order submission protocol",
      "blind": true
    },
    {
      "id": "B",
      "executor": "codex gpt-5.5 spawn_agent",
      "revision": "afaaa2a0116327b2c74fd9a54be5ab258c4ffb57",
      "angles": ["errors", "concurrency", "tests"],
      "hotspot": "payment retry identity",
      "blind": true
    }
  ],
  "angles": {
    "requirements": { "evidence": "CheckoutPage production path traced; 4 entry points exercised" },
    "errors":       { "evidence": "..." },
    "concurrency":  { "evidence": "..." },
    "security":     { "evidence": "..." },
    "callers":      { "evidence": "..." },
    "tests":        { "not_applicable": "docs-only change; no test surface" }
  },
  "reviewer_reports": {
    "A": { "confirmed": ["A1"], "pending": [], "rejected": [] },
    "B": { "confirmed": [], "pending": ["B2"], "rejected": ["B1"] }
  },
  "candidates": [
    {
      "id": "C1",
      "sources": ["A", "primary"],
      "source_items": ["A1"],
      "title": "Cancel during payment-lock wait still charges and leaves NOT_FOUND",
      "location": "src/checkout/use-checkout.ts:686-692",
      "disposition": "confirmed",
      "severity": "should_fix",
      "cause": "introduced",
      "evidence": "node -e harness, 4/4 entry points, exit 1 on no-error assertion",
      "origin": "missed-earlier",
      "origin_detail": "present since 7893951d; matrix row 'submission cancel' lacked the lock-wait cell"
    },
    {
      "id": "C2",
      "sources": ["B"],
      "source_items": ["B1"],
      "title": "Legacy hook loses cancel when cart is null",
      "location": "...",
      "disposition": "rejected",
      "refutation": "CheckoutPage.tsx:140 is the only production caller and always passes a cart object"
    },
    {
      "id": "C3",
      "sources": ["B"],
      "source_items": ["B2"],
      "title": "Cancel operation id reuse across retries",
      "location": "...",
      "disposition": "pending",
      "missing_evidence": "backend idempotency scope not readable from this repo",
      "blocks_pass": false
    }
  ],
  "coverage_gaps": ["real Next cache behaviour not run on exact head"]
}
```

## Fields

- `verdict` is the **code-review** decision, not a combined merge/release decision. `coverage_gaps` and candidate `blocks_pass` refer to evidence material to code correctness. A defect shown by a non-required check still blocks code; a delivery-only failed check does not.
- `delivery` is required for new PR reports; optional for compatibility with older records. It has `status` in `READY|BLOCKED|WAITING|UNVERIFIED|NOT_APPLICABLE`, a string list `blockers` naming actual platform-required or explicit project conditions and their sources, and a string list `advisories` for other checks/remaining acceptance work. `READY` and `NOT_APPLICABLE` cannot have blockers; `BLOCKED`/`WAITING`/`UNVERIFIED` require a named blocker or unknown condition. Local-only review uses `NOT_APPLICABLE`. Unknown platform policy is `UNVERIFIED`, not “all CI required”. The checker validates structure, not whether the cited platform policy is real.
- `PASS` with delivery `BLOCKED` or `WAITING` is valid: authorized code approval can proceed with the conditions disclosed, unless a repository explicitly makes one a code-approval prerequisite. Approval does not bypass those conditions or certify QA/release. Missing UI/runtime proof belongs to `coverage_gaps` only when it prevents establishing code correctness; otherwise disclose it in `delivery`.
- `panel`: `quick` (2 reviewers) or `full` (6 reviewers); the count must match exactly. `none` when the independent review trigger did not fire; then `reviewers` is empty and the angle check still applies to the primary.
- `verdict_kind`: `independent`, or `consolidated-recheck` when the primary authored or edited any part of the change. A consolidated recheck always has a panel.
- `primary.skill_version`: the skill version that wrote the record. Fields a later version added are required only from that version on (`cause` from 3.15.0); a record without a parseable version is checked as current.
- `reviewers[].id`: non-empty, unique, never `primary` (reserved for the adjudicating reviewer in `sources`).
- `reviewers[].angles`: subset of the six angle keys. Across the panel every angle must be owned by at least one reviewer.
- `reviewers[].revision`: must equal the top-level `revision`; a reviewer on another revision is a stale opinion, not panel evidence.
- `reviewers[].blind`: must be `true`; a reviewer who saw the primary's conclusions or another reviewer's report is not a panel reviewer and is left out of the record.
- `reviewer_reports`: one entry per reviewer, the item ids of its original `confirmed` / `pending` / `rejected` lists before adjudication. Item ids are unique across the record. The "independent conclusion" counts in the report are derived from here.
- `angles`: all six keys required: `requirements`, `errors`, `concurrency`, `security`, `callers`, `tests`. Each has `evidence` (what was checked, in one line) or `not_applicable` (why), never both.
- `candidates[].sources`: reviewer ids and/or `primary`. `source_items` lists the reviewer items merged into this candidate; every reviewer item must land in exactly one candidate (nothing dropped, nothing double-counted), and every non-primary source must contribute at least one item.
- `candidates[].disposition`: `confirmed` (needs `severity` in `must_fix|should_fix|suggestion` and `evidence`), `rejected` (needs `refutation` naming the code), or `pending` (needs `missing_evidence` and `blocks_pass`).
- `candidates[].cause` (confirmed only; required from 3.15.0): `introduced`, `regression`, or `pre-existing` (SKILL.md step 3). A `pre-existing` candidate is a `suggestion` and never blocks this change; it cannot carry `origin: introduced-by-fix`, because a fix commit of this change did not exist at the base.
- `candidates[].accepted_risk`: on a confirmed `should_fix` only, who accepted the risk and where it is recorded (PR comment, message); with it the candidate no longer blocks `PASS`. A `must_fix` can never be risk-accepted.
- `candidates[].origin` (round ≥ 2, confirmed only): `introduced-by-fix`, `missed-earlier`, `pending-confirmed` (an earlier round's pending candidate now confirmed by new evidence), or `carried-over` (reported in an earlier round and still unresolved; needs `first_round`). `origin_detail` names the sha and, for `missed-earlier`, the entry, state, or assumption that was missed — or `unknown` when it genuinely is; a `pre-existing` finding names the base sha only.
- `coverage_gaps`: material gaps the primary found outside the candidate list; non-empty forbids `PASS`.

## Contradictions the checker rejects

- `round` outside `1`–`7`: there is no `8/7`; a human-authorized continuation starts a new `cycle_id` at round `1`.
- `verdict: PASS` with a confirmed `must_fix`, a confirmed `should_fix` without `accepted_risk`, a `pending` candidate with `blocks_pass: true`, or any `coverage_gaps`.
- A malformed `delivery`, a ready/not-applicable delivery with blockers, or a blocked/waiting/unverified delivery with no explanation. A passing code verdict with delivery blockers is **not** a contradiction.
- `verdict_kind: consolidated-recheck` with `panel: none`.
- Reviewer count different from the panel size, duplicate or reserved reviewer ids, a reviewer on another revision, a non-blind reviewer, a reviewer with no angles, an angle nobody owns, or a reviewer without a `reviewer_reports` entry.
- An angle with neither `evidence` nor `not_applicable`, or with both.
- A candidate missing the fields its disposition requires, an unknown source, a `source_item` not in any report or attached to two candidates, a source that contributed no item, or a reviewer item no candidate adjudicated.
- A confirmed candidate without a `cause` (records from 3.15.0 on), or a `pre-existing` candidate graded above `suggestion` or carrying `origin: introduced-by-fix`.
- Round ≥ 2 and a confirmed candidate without `origin`; `carried-over` without a valid `first_round`; a risk-accepted `must_fix`.
