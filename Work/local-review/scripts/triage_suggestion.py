#!/usr/bin/env python3
"""Triage one low-severity review suggestion with the TypeSafe Jev model.

Decides whether a `suggestion` (or an unsure finding) is worth fixing before
anyone spends a commit, an approval and a CI run on it.

    uv run --with typesafe-sdk python -I scripts/triage_suggestion.py input.json
    python3 scripts/triage_suggestion.py input.json --print-request   # no network

Input JSON: {"suggestion": str, "code": str | [str], "facts": [str, ...]}
Output JSON: {"model", "answers", "decision", "thresholds"}; decision is FIX, SKIP or ASK_HUMAN.
The API key is read from TYPESAFE_API_KEY by the SDK and is never printed.
"""

import argparse
import json
import re
import sys

HIGH = 0.7  # every answer at or above this: fix
LOW = 0.3  # any answer at or below this: skip
MIN_FACTS = 3
SECRET = re.compile(
    r"(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|eyJ[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{30,})"
)

QUESTIONS = {
    "failure_reachable": {
        "instructions": (
            "Could the failure this suggestion guards against occur in normal operation of this code, "
            "not only in contrived or adversarial situations?"
        ),
        "criteria": {
            "true": "Plausible during ordinary runs",
            "false": "Needs a contrived or extremely unlikely event",
        },
    },
    "change_achieves_goal": {
        "instructions": (
            "In the failure scenario described under facts, would the proposed change actually deliver "
            "its stated benefit?"
        ),
        "criteria": {
            "true": "The change works as intended in that scenario",
            "false": "The scenario defeats the change, so the benefit is not delivered",
        },
    },
    "worth_the_cost": {
        "instructions": "Is the benefit of the change worth the cost listed under facts?",
    },
}


def validate(data: object) -> dict:
    """Return the state to send, or raise ValueError with a message safe to print."""
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    suggestion = data.get("suggestion")
    code = data.get("code")
    facts = data.get("facts")
    if not isinstance(suggestion, str) or not suggestion.strip():
        raise ValueError("suggestion must be a non-empty string")
    if isinstance(code, str):
        code = [code]
    if not isinstance(code, list) or not code or not all(isinstance(line, str) for line in code):
        raise ValueError("code must be a non-empty string or list of strings")
    if not isinstance(facts, list) or not all(isinstance(fact, str) and fact.strip() for fact in facts):
        raise ValueError("facts must be a list of non-empty strings")
    if len(facts) < MIN_FACTS:
        raise ValueError(
            f"give at least {MIN_FACTS} verified facts (reachability, what the cleanup/fallback path does, cost of fixing)"
        )
    state = {"suggestion": suggestion, "code": code, "facts": facts}
    if SECRET.search(json.dumps(state)):
        raise ValueError("input looks like it contains a secret or token; remove it before sending to an external service")
    return state


def decide(answers: dict[str, float]) -> str:
    """FIX only when every judgment is a clear yes; SKIP when any is a clear no; otherwise a person decides."""
    if set(answers) != set(QUESTIONS):
        raise ValueError("answers must cover exactly the triage questions")
    if all(value >= HIGH for value in answers.values()):
        return "FIX"
    if any(value <= LOW for value in answers.values()):
        return "SKIP"
    return "ASK_HUMAN"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input")
    parser.add_argument("--print-request", action="store_true", help="show exactly what would be sent, then stop")
    args = parser.parse_args()
    try:
        with open(args.input, encoding="utf-8") as handle:
            state = validate(json.load(handle))
    except (OSError, ValueError) as error:
        print(f"input error: {error}", file=sys.stderr)
        return 2
    if args.print_request:
        print(json.dumps({"model": "jev-latest", "state": state, "questions": QUESTIONS}, ensure_ascii=False, indent=2))
        return 0
    try:
        from typesafe_sdk import Noul, NoulCriteria, TypeSafeClient
    except ImportError:
        print("typesafe-sdk is missing; run with: uv run --with typesafe-sdk python -I <this script> <input>", file=sys.stderr)
        return 3
    questions = {
        key: Noul(
            instructions=spec["instructions"],
            **({"criteria": NoulCriteria(**spec["criteria"])} if "criteria" in spec else {}),
        )
        for key, spec in QUESTIONS.items()
    }
    try:
        with TypeSafeClient() as client:
            response = client.system_one(model="jev-latest", state=state, questions=questions)
    except Exception as error:  # SDK raises its own error types; never print request data or credentials.
        print(f"TypeSafe call failed: {type(error).__name__}", file=sys.stderr)
        return 3
    answers = {key: round(answer.noul, 3) for key, answer in response.nouls.items()}
    print(
        json.dumps(
            {
                "model": response.model,
                "answers": answers,
                "decision": decide(answers),
                "thresholds": {"fix_at_least": HIGH, "skip_at_most": LOW},
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
