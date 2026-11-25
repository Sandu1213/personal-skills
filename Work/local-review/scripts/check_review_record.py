#!/usr/bin/env python3
"""Check a local-review record (references/review-record.md) for missing items and contradictions.

Usage: check_review_record.py <record.json | ->
`-` reads the record from stdin for sandboxes where no path is writable.
Exit 0 when consistent; exit 1 and list every problem otherwise.
Consistency of the record only: this proves nothing about whether the code was read.
"""
import json
import sys

ANGLES = ("requirements", "errors", "concurrency", "security", "callers", "tests")
PANEL_SIZE = {"none": 0, "quick": 2, "full": 6}
SEVERITIES = ("must_fix", "should_fix", "suggestion")
ORIGINS = ("introduced-by-fix", "missed-earlier", "pending-confirmed", "carried-over")
CAUSES = ("introduced", "regression", "pre-existing")
CAUSE_SINCE = (3, 15, 0)  # records written by older skill versions predate `cause`
LISTS = ("confirmed", "pending", "rejected")


def nonempty_str(v):
    return isinstance(v, str) and v.strip() != ""


def skill_version(rec):
    """`primary.skill_version` as an int tuple, or None when absent or unparseable."""
    primary = rec.get("primary")
    v = primary.get("skill_version") if isinstance(primary, dict) else None
    if not isinstance(v, str):
        return None
    try:
        parts = tuple(int(part) for part in v.split("."))
    except ValueError:
        return None
    return parts + (0,) * (3 - len(parts))  # "3.15" compares as 3.15.0


def check(rec):
    p = []
    if not isinstance(rec, dict):
        return ["record must be a JSON object"]
    for key in ("cycle_id", "revision"):
        if not nonempty_str(rec.get(key)):
            p.append(f"'{key}' must be a non-empty string")
    rnd = rec.get("round")
    if not isinstance(rnd, int) or isinstance(rnd, bool) or not 1 <= rnd <= 7:
        p.append("'round' must be an integer in [1, 7]; 8/7 does not exist, start a new cycle")
    panel = rec.get("panel")
    if panel not in PANEL_SIZE:
        p.append(f"'panel' must be one of {list(PANEL_SIZE)}, got {panel!r}")
    verdict = rec.get("verdict")
    if verdict not in ("PASS", "BLOCK", "UNVERIFIED"):
        p.append(f"'verdict' must be PASS/BLOCK/UNVERIFIED, got {verdict!r}")
    kind = rec.get("verdict_kind")
    if kind not in ("independent", "consolidated-recheck"):
        p.append(f"'verdict_kind' must be independent/consolidated-recheck, got {kind!r}")
    for key in ("reviewers", "candidates", "coverage_gaps"):
        if not isinstance(rec.get(key, []), list):
            p.append(f"'{key}' must be a list")
    if not isinstance(rec.get("angles"), dict):
        p.append("'angles' must be an object")
    if not isinstance(rec.get("reviewer_reports", {}), dict):
        p.append("'reviewer_reports' must be an object")
    if p:
        return p
    assert isinstance(rnd, int) and isinstance(panel, str)  # validated above; narrows for type checkers
    written_by = skill_version(rec)
    cause_required = written_by is None or written_by >= CAUSE_SINCE

    # Code acceptance and delivery readiness are independent. Older records omit delivery.
    if "delivery" in rec:
        delivery = rec["delivery"]
        if not isinstance(delivery, dict):
            p.append("'delivery' must be an object")
        else:
            status = delivery.get("status")
            statuses = ("READY", "BLOCKED", "WAITING", "UNVERIFIED", "NOT_APPLICABLE")
            if status not in statuses:
                p.append(f"delivery.status must be one of {statuses}")
            for key in ("blockers", "advisories"):
                values = delivery.get(key)
                if not isinstance(values, list) or any(not nonempty_str(v) for v in values):
                    p.append(f"delivery.{key} must be a list of non-empty strings")
            blockers = delivery.get("blockers")
            if isinstance(blockers, list):
                if status in ("READY", "NOT_APPLICABLE") and blockers:
                    p.append(f"delivery {status} cannot have delivery blockers")
                if status in ("BLOCKED", "WAITING", "UNVERIFIED") and not blockers:
                    p.append(f"delivery {status} needs a delivery blocker or unknown condition")

    revision = rec["revision"]
    reviewers = rec.get("reviewers", [])
    reports = rec.get("reviewer_reports", {})
    ids = []
    owned = set()
    for i, r in enumerate(reviewers):
        if not isinstance(r, dict) or not nonempty_str(r.get("id")):
            p.append(f"reviewers[{i}] needs a non-empty string id")
            continue
        rid = r["id"]
        ids.append(rid)
        if rid == "primary":
            p.append("reviewer id 'primary' is reserved for the adjudicating reviewer")
        if r.get("revision") != revision:
            p.append(f"reviewer {rid} revision {r.get('revision')!r} != record revision")
        if not nonempty_str(r.get("executor")):
            p.append(f"reviewer {rid} has no executor")
        if r.get("blind") is not True:
            p.append(f"reviewer {rid} is not blind; a non-blind reviewer is not panel evidence")
        angles = r.get("angles")
        if not isinstance(angles, list) or not angles:
            p.append(f"reviewer {rid} owns no angle")
        else:
            for a in angles:
                if a not in ANGLES:
                    p.append(f"reviewer {rid} names unknown angle {a!r}")
                owned.add(a)
        if rid not in reports:
            p.append(f"reviewer {rid} has no entry in reviewer_reports")
    if len(ids) != len(set(ids)):
        p.append("duplicate reviewer ids")
    size = PANEL_SIZE[panel]
    if len(reviewers) != size:
        p.append(f"panel '{panel}' needs exactly {size} reviewers, record has {len(reviewers)}")
    if reviewers:
        for a in ANGLES:
            if a not in owned:
                p.append(f"angle '{a}' is owned by no reviewer")
    if kind == "consolidated-recheck" and panel == "none":
        p.append("a consolidated recheck needs at least a quick panel")

    # original per-reviewer verdicts: every item must land in exactly one candidate
    items = {}
    for rid, rep in reports.items():
        if rid not in ids:
            p.append(f"reviewer_reports names unknown reviewer {rid!r}")
            continue
        if not isinstance(rep, dict):
            p.append(f"reviewer_reports[{rid}] must be an object with {LISTS}")
            continue
        for lst in LISTS:
            vals = rep.get(lst)
            if not isinstance(vals, list):
                p.append(f"reviewer_reports[{rid}].{lst} must be a list")
                continue
            for item in vals:
                if not nonempty_str(item):
                    p.append(f"reviewer_reports[{rid}].{lst} has a non-string item")
                elif item in items:
                    p.append(f"reviewer item {item!r} listed twice")
                else:
                    items[item] = rid

    angles = rec["angles"]
    for a in ANGLES:
        entry = angles.get(a)
        if not isinstance(entry, dict):
            p.append(f"angle '{a}' missing")
            continue
        has_ev, has_na = nonempty_str(entry.get("evidence")), nonempty_str(entry.get("not_applicable"))
        if has_ev == has_na:
            p.append(f"angle '{a}' needs exactly one of evidence / not_applicable")

    known_sources = set(ids) | {"primary"}
    cids = []
    blocking = []
    seen_items = set()
    for i, c in enumerate(rec["candidates"]):
        if not isinstance(c, dict) or not nonempty_str(c.get("id")):
            p.append(f"candidates[{i}] needs a non-empty string id")
            continue
        cid = c["id"]
        cids.append(cid)
        sources = c.get("sources")
        if not isinstance(sources, list) or not sources:
            p.append(f"candidate {cid} has no sources")
            sources = []
        for s in sources:
            if s not in known_sources:
                p.append(f"candidate {cid} source {s!r} is not a reviewer or 'primary'")
        src_items = c.get("source_items", [])
        if not isinstance(src_items, list):
            p.append(f"candidate {cid} source_items must be a list")
            src_items = []
        for item in src_items:
            if item not in items:
                p.append(f"candidate {cid} source_item {item!r} is not in any reviewer report")
            elif items[item] not in sources:
                p.append(f"candidate {cid} source_item {item!r} belongs to reviewer {items[item]} not in sources")
            elif item in seen_items:
                p.append(f"reviewer item {item!r} is attached to more than one candidate")
            seen_items.add(item)
        for s in sources:
            if s != "primary" and not any(items.get(it) == s for it in src_items):
                p.append(f"candidate {cid} names source {s} but no source_item from {s}")
        if not nonempty_str(c.get("location")):
            p.append(f"candidate {cid} has no location")
        d = c.get("disposition")
        if d == "confirmed":
            sev = c.get("severity")
            if sev not in SEVERITIES:
                p.append(f"candidate {cid} confirmed without severity in {SEVERITIES}")
            if not nonempty_str(c.get("evidence")):
                p.append(f"candidate {cid} confirmed without evidence")
            cause = c.get("cause")
            if cause not in CAUSES:
                if cause is not None or cause_required:
                    p.append(f"candidate {cid} confirmed without cause in {CAUSES}")
            elif cause == "pre-existing":
                if sev != "suggestion":
                    p.append(f"candidate {cid}: a pre-existing finding is a suggestion and cannot block this change")
                if c.get("origin") == "introduced-by-fix":
                    p.append(f"candidate {cid}: pre-existing contradicts origin introduced-by-fix")
            accepted = c.get("accepted_risk")
            if sev == "must_fix":
                if accepted:
                    p.append(f"candidate {cid}: must_fix cannot be risk-accepted")
                blocking.append(cid)
            elif sev == "should_fix":
                if accepted is None:
                    blocking.append(cid)
                elif not nonempty_str(accepted):
                    p.append(f"candidate {cid} accepted_risk must name who accepted it and where")
            if rnd >= 2:
                origin = c.get("origin")
                if origin not in ORIGINS:
                    p.append(f"candidate {cid} confirmed in round {rnd} without origin in {ORIGINS}")
                elif origin == "carried-over":
                    fr = c.get("first_round")
                    if not isinstance(fr, int) or isinstance(fr, bool) or not 1 <= fr < rnd:
                        p.append(f"candidate {cid} carried-over needs first_round in [1, {rnd - 1}]")
                elif not nonempty_str(c.get("origin_detail")):
                    p.append(f"candidate {cid} has origin but no origin_detail")
        elif d == "rejected":
            if not nonempty_str(c.get("refutation")):
                p.append(f"candidate {cid} rejected without refutation")
        elif d == "pending":
            if not nonempty_str(c.get("missing_evidence")):
                p.append(f"candidate {cid} pending without missing_evidence")
            if not isinstance(c.get("blocks_pass"), bool):
                p.append(f"candidate {cid} pending without boolean blocks_pass")
            elif c["blocks_pass"]:
                blocking.append(cid)
        else:
            p.append(f"candidate {cid} disposition must be confirmed/rejected/pending, got {d!r}")
    if len(cids) != len(set(cids)):
        p.append("duplicate candidate ids")
    for item, rid in items.items():
        if item not in seen_items:
            p.append(f"reviewer {rid} item {item!r} was never adjudicated")

    gaps = rec.get("coverage_gaps", [])
    if verdict == "PASS":
        if blocking:
            p.append(f"PASS contradicts unresolved candidates {blocking}")
        if gaps:
            p.append(f"PASS contradicts coverage_gaps {gaps}")
    return p


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    if argv[1] == "-":
        rec = json.load(sys.stdin)
    else:
        with open(argv[1], encoding="utf-8") as f:
            rec = json.load(f)
    problems = check(rec)
    for line in problems:
        print(f"- {line}")
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
