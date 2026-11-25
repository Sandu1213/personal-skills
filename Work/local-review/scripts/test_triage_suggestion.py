#!/usr/bin/env python3
"""Tests for triage_suggestion.py (no network). Run: python3 scripts/test_triage_suggestion.py"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from triage_suggestion import HIGH, LOW, QUESTIONS, decide, validate  # noqa: E402

FACTS = ["it is test code", "cleanup reuses the same connection", "a fix needs a new commit and a CI rerun"]


def good(**overrides):
    data = {"suggestion": "move the lookup into try", "code": ["a = 1"], "facts": list(FACTS)}
    data.update(overrides)
    return data


def answers(a, b, c):
    return dict(zip(QUESTIONS, (a, b, c)))


class DecideTests(unittest.TestCase):
    def test_fix_needs_every_answer_at_the_high_threshold(self):
        self.assertEqual(decide(answers(HIGH, 0.95, 0.9)), "FIX")
        self.assertEqual(decide(answers(HIGH, 0.95, HIGH - 0.01)), "ASK_HUMAN")

    def test_one_clear_no_skips_even_when_the_others_are_yes(self):
        self.assertEqual(decide(answers(0.99, 0.99, LOW)), "SKIP")
        self.assertEqual(decide(answers(0.99, 0.99, LOW + 0.01)), "ASK_HUMAN")

    def test_the_middle_band_goes_to_a_person(self):
        self.assertEqual(decide(answers(0.5, 0.5, 0.5)), "ASK_HUMAN")

    def test_answers_must_cover_exactly_the_questions(self):
        with self.assertRaises(ValueError):
            decide({"failure_reachable": 0.9})


class ValidateTests(unittest.TestCase):
    def test_accepts_a_complete_input_and_normalises_string_code(self):
        self.assertEqual(validate(good(code="a = 1"))["code"], ["a = 1"])

    def test_rejects_missing_or_thin_input(self):
        for bad in (
            [],
            good(suggestion=" "),
            good(code=[]),
            good(code=[1]),
            good(facts=FACTS[:2]),
            good(facts=["ok", " ", "x"]),
        ):
            with self.assertRaises(ValueError):
                validate(bad)

    def test_refuses_to_send_secrets(self):
        for secret in ("sk-" + "a" * 24, "AKIA" + "A" * 16, "-----BEGIN RSA PRIVATE KEY-----"):
            with self.assertRaises(ValueError):
                validate(good(code=[f"token = '{secret}'"]))


class CliTests(unittest.TestCase):
    def run_cli(self, data, *flags):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump(data, handle)
        try:
            return subprocess.run(
                [sys.executable, os.path.join(HERE, "triage_suggestion.py"), handle.name, *flags],
                capture_output=True,
                text=True,
            )
        finally:
            os.unlink(handle.name)

    def test_print_request_shows_the_payload_without_a_network_call(self):
        result = self.run_cli(good(), "--print-request")
        self.assertEqual(result.returncode, 0, result.stderr)
        request = json.loads(result.stdout)
        self.assertEqual(request["state"]["suggestion"], "move the lookup into try")
        self.assertEqual(set(request["questions"]), set(QUESTIONS))

    def test_bad_input_exits_2_with_a_message(self):
        result = self.run_cli(good(facts=[]), "--print-request")
        self.assertEqual(result.returncode, 2)
        self.assertIn("input error", result.stderr)


if __name__ == "__main__":
    unittest.main()
