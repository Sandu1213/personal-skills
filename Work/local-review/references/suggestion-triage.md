# Suggestion triage

Decide whether a low-severity review item is worth fixing **before** spending a commit, an approval and a CI run on it. A fix that dismisses an existing approval and reruns CI is not free, and many `suggestion`-level items turn out to guard a failure that cannot happen or to be defeated by the very scenario they target.

## When to use it

- Use for a `suggestion`, and for an item the author is unsure is worth changing.
- Do **not** use it for `must_fix` or `should_fix`: those are decided by evidence and by the user's explicit risk acceptance, never by a probability. A low score cannot downgrade or dismiss them. Nor for a `pre-existing` finding: its fix belongs to a separate task, not this change.
- It never replaces the refutation step in "Produce the verdict": a finding is removed only when the code proves it wrong.

## How it works

[`triage_suggestion.py`](../scripts/triage_suggestion.py) asks the TypeSafe Jev model three independent yes/no questions (Noul, probability of yes) over one state: the suggestion, the code, and verified facts.

| Question | Meaning |
| --- | --- |
| `failure_reachable` | Can the guarded failure occur in normal operation, not only in contrived situations? |
| `change_achieves_goal` | In that failure scenario, does the proposed change actually deliver its stated benefit? |
| `worth_the_cost` | Is the benefit worth the listed cost (another commit, dismissed approval, CI rerun)? |

Decision (`HIGH = 0.7`, `LOW = 0.3`, the starting points from the TypeSafe docs, not calibrated on our data):

- every answer at least `HIGH` -> `FIX`
- any answer at most `LOW` -> `SKIP`
- otherwise -> `ASK_HUMAN`; a person decides, with the three numbers in front of them

## Running it

```bash
# the key is read from TYPESAFE_API_KEY and is never printed
uv run --with typesafe-sdk python -I scripts/triage_suggestion.py input.json
python3 scripts/triage_suggestion.py input.json --print-request   # show what would be sent, no network
```

Input: `{"suggestion": "...", "code": ["...", "..."], "facts": ["...", "...", "..."]}`. At least three facts are required. Exit code 2 is an input problem (including a secret-looking value, which is refused), 3 is a TypeSafe or SDK failure.

## Writing the facts

The model judges the state you write, not the repository. A wrong or missing fact gives a confident wrong answer, so:

- Verify each fact against the code first; write only what you checked.
- Always include: whether the failure can happen in ordinary runs, what the cleanup/fallback path does in that failure (for example, which connection or resource it reuses), how the environment limits the damage (disposable CI service, retry, etc.), whether a test covers the change, and the cost of pushing the fix (dismissed approval, CI rerun).
- Send the smallest code excerpt that makes the question answerable. Never include credentials, tokens or user data. The content goes to an external service; use `--print-request` first when unsure.

## Recording the result

Put the three probabilities, the model name and the decision in the candidate's `evidence` (or in the PR/report text for a suggestion that is not in a record). A `SKIP` is reported as "not worth fixing, reason" and the suggestion stays a `suggestion`; it is not deleted. A `FIX` or an `ASK_HUMAN` still needs the author or user to choose the fix.

## Limits

- Results near a threshold are sensitive to wording: rerunning the same case with slightly reworded criteria moved the answers from `0.29 / 0.21 / 0.32` to `0.27 / 0.34 / 0.33` with the same decision. Treat anything within about `0.05` of a threshold as borderline and prefer `ASK_HUMAN`.
- Typed output guarantees the shape, not the truth. Validate the thresholds on real review items before relying on them for more than triage.
