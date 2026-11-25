#!/usr/bin/env python3
"""Regression tests for check_review_record.py. Run: python3 scripts/test_check_review_record.py"""
import copy
import json
import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_review_record import check  # noqa: E402

REF = os.path.join(HERE, "..", "references", "review-record.md")


def example():
    with open(REF, encoding="utf-8") as f:
        text = f.read()
    match = re.search(r"```json\n(.*?)\n```", text, re.S)
    assert match, "review-record.md has no json example"
    return json.loads(match.group(1))


class ReviewRecordCheck(unittest.TestCase):
    def setUp(self):
        self.rec = example()

    def assertProblem(self, rec, fragment):
        problems = check(rec)
        self.assertTrue(any(fragment in x for x in problems), f"expected {fragment!r} in {problems}")

    def test_documented_example_is_consistent(self):
        self.assertEqual(check(self.rec), [])

    def test_stdin_cli_path(self):
        r = subprocess.run(
            [sys.executable, os.path.join(HERE, "check_review_record.py"), "-"],
            input=json.dumps(self.rec), capture_output=True, text=True,
        )
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "OK"))

    def test_clean_pass_is_accepted(self):
        rec = self.rec
        rec["verdict"] = "PASS"
        rec["coverage_gaps"] = []
        rec["candidates"] = [c for c in rec["candidates"] if c["disposition"] == "rejected"]
        rec["reviewer_reports"] = {"A": {"confirmed": [], "pending": [], "rejected": []},
                                   "B": {"confirmed": [], "pending": [], "rejected": ["B1"]}}
        self.assertEqual(check(rec), [])

    def test_pass_contradicts_blocking_candidate_and_gap(self):
        rec = self.rec
        rec["verdict"] = "PASS"
        self.assertProblem(rec, "PASS contradicts unresolved candidates")
        self.assertProblem(rec, "PASS contradicts coverage_gaps")

    def test_accepted_should_fix_does_not_block_but_must_fix_does(self):
        rec = self.rec
        rec["verdict"] = "PASS"
        rec["coverage_gaps"] = []
        rec["candidates"][2]["blocks_pass"] = False
        rec["candidates"][0]["accepted_risk"] = "user, 2026-11-04, PR comment"
        self.assertEqual(check(rec), [])
        rec["candidates"][0]["severity"] = "must_fix"
        self.assertProblem(rec, "must_fix cannot be risk-accepted")

    def test_carried_over_needs_first_round(self):
        rec = self.rec
        rec["candidates"][0]["origin"] = "carried-over"
        self.assertProblem(rec, "carried-over needs first_round")
        rec["candidates"][0]["first_round"] = 1
        self.assertEqual(check(rec), [])

    def test_round_stays_within_seven(self):
        for rnd in (0, 8, True):
            rec = copy.deepcopy(self.rec)
            rec["round"] = rnd
            self.assertProblem(rec, "'round' must be an integer in [1, 7]")
        self.rec["round"] = 7
        self.assertEqual(check(self.rec), [])

    def test_missing_identities_and_wrong_containers(self):
        rec = copy.deepcopy(self.rec)
        rec["revision"] = ""
        self.assertProblem(rec, "'revision' must be a non-empty string")
        rec = copy.deepcopy(self.rec)
        rec["candidates"] = {}
        self.assertProblem(rec, "'candidates' must be a list")
        rec = copy.deepcopy(self.rec)
        del rec["candidates"][0]["id"]
        self.assertProblem(rec, "candidates[0] needs a non-empty string id")
        rec = copy.deepcopy(self.rec)
        rec["reviewers"][0]["id"] = "primary"
        self.assertProblem(rec, "reserved")

    def test_panel_declarations(self):
        rec = copy.deepcopy(self.rec)
        rec["reviewers"][0]["blind"] = False
        self.assertProblem(rec, "is not blind")
        rec = copy.deepcopy(self.rec)
        rec["reviewers"].append(dict(rec["reviewers"][0], id="C"))
        self.assertProblem(rec, "needs exactly 2 reviewers")
        rec = copy.deepcopy(self.rec)
        rec["verdict_kind"] = "consolidated-recheck"
        rec["panel"] = "none"
        rec["reviewers"] = []
        rec["reviewer_reports"] = {}
        for c in rec["candidates"]:
            c["sources"] = ["primary"]
            c["source_items"] = []
        self.assertProblem(rec, "consolidated recheck needs at least a quick panel")

    def test_reviewer_items_cannot_be_dropped_or_double_counted(self):
        rec = copy.deepcopy(self.rec)
        rec["reviewer_reports"]["B"]["pending"].append("B9")
        self.assertProblem(rec, "item 'B9' was never adjudicated")
        rec = copy.deepcopy(self.rec)
        rec["candidates"][1]["source_items"].append("B1")
        self.assertProblem(rec, "attached to more than one candidate")

    def test_stale_reviewer_revision_and_unknown_source(self):
        rec = copy.deepcopy(self.rec)
        rec["reviewers"][1]["revision"] = "deadbeef"
        self.assertProblem(rec, "!= record revision")
        rec = copy.deepcopy(self.rec)
        rec["candidates"][2]["sources"] = ["Z"]
        self.assertProblem(rec, "source 'Z' is not a reviewer")

    def _clean_pass(self):
        rec = copy.deepcopy(self.rec)
        rec["verdict"] = "PASS"
        rec["coverage_gaps"] = []
        rec["candidates"][0]["accepted_risk"] = "user, PR comment"
        rec["candidates"][2]["blocks_pass"] = False
        self.assertEqual(check(rec), [])
        return rec

    def test_code_pass_can_coexist_with_delivery_blockers(self):
        for status in ("BLOCKED", "WAITING", "UNVERIFIED"):
            with self.subTest(status=status):
                rec = self._clean_pass()
                rec["delivery"] = {
                    "status": status,
                    "blockers": ["branch rules: required CI not successful"],
                    "advisories": ["release QA not performed"],
                }
                self.assertEqual(check(rec), [])

    def test_delivery_ready_cannot_hide_blockers(self):
        for status in ("READY", "NOT_APPLICABLE"):
            with self.subTest(status=status):
                rec = self._clean_pass()
                rec["delivery"] = {
                    "status": status, "blockers": ["required CI failed"], "advisories": [],
                }
                self.assertProblem(rec, "cannot have delivery blockers")

    def test_delivery_condition_requires_explanation(self):
        for status in ("BLOCKED", "WAITING", "UNVERIFIED"):
            with self.subTest(status=status):
                rec = copy.deepcopy(self.rec)
                rec["delivery"] = {"status": status, "blockers": [], "advisories": []}
                self.assertProblem(rec, "needs a delivery blocker or unknown condition")

    def test_delivery_shape_and_legacy_compatibility(self):
        rec = self._clean_pass()
        rec.pop("delivery", None)
        self.assertEqual(check(rec), [])
        for delivery in (None, [], {"status": "green"},
                         {"status": "READY", "blockers": [], "advisories": "none"}):
            with self.subTest(delivery=delivery):
                rec["delivery"] = delivery
                self.assertProblem(rec, "delivery")

    def test_must_fix_alone_blocks_pass(self):
        rec = self._clean_pass()
        del rec["candidates"][0]["accepted_risk"]
        rec["candidates"][0]["severity"] = "must_fix"
        self.assertProblem(rec, "PASS contradicts unresolved candidates ['C1']")

    def test_blocking_pending_alone_blocks_pass(self):
        rec = self._clean_pass()
        rec["candidates"][2]["blocks_pass"] = True
        self.assertProblem(rec, "PASS contradicts unresolved candidates ['C3']")

    def test_confirmed_needs_cause_and_pre_existing_never_blocks(self):
        rec = copy.deepcopy(self.rec)
        del rec["candidates"][0]["cause"]
        self.assertProblem(rec, "confirmed without cause")
        rec["candidates"][0]["cause"] = "pre-existing"
        self.assertProblem(rec, "a pre-existing finding is a suggestion")
        rec["candidates"][0]["severity"] = "suggestion"
        rec["candidates"][0]["origin"] = "introduced-by-fix"
        self.assertProblem(rec, "pre-existing contradicts origin introduced-by-fix")
        rec["candidates"][0]["origin"] = "missed-earlier"
        rec["verdict"], rec["coverage_gaps"] = "PASS", []
        self.assertEqual(check(rec), [])

    def test_cause_is_required_from_3_15_0(self):
        rec = copy.deepcopy(self.rec)
        del rec["candidates"][0]["cause"]
        rec["primary"]["skill_version"] = "3.14.0"
        self.assertEqual(check(rec), [])  # written before `cause` existed
        rec["candidates"][0]["cause"] = "unknown"
        self.assertProblem(rec, "confirmed without cause")  # a present cause is still validated
        del rec["candidates"][0]["cause"]
        for version in ("3.15.0", "3.15", "4.0.0", "3.15.x"):
            rec["primary"]["skill_version"] = version
            self.assertProblem(rec, "confirmed without cause")
        del rec["primary"]["skill_version"]
        self.assertProblem(rec, "confirmed without cause")

    def test_source_item_must_belong_to_a_listed_source(self):
        rec = copy.deepcopy(self.rec)
        rec["candidates"][0]["source_items"] = ["B1"]  # B1 is B's item, but sources are A + primary
        self.assertProblem(rec, "source_item 'B1' belongs to reviewer B not in sources")


if __name__ == "__main__":
    unittest.main()
