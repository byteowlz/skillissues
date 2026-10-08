"""Synthetic contract tests; no external mutation or evidence execution."""

import io
import json
import unittest

from jsonschema import Draft202012Validator

from validate_report import SCHEMA, run, validate_report


def fixture():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return {
        "schema_version": "agent-readiness/v1", "project": "synthetic-demo",
        "revision": "fixture-v1", "scope": "Report validator fixture, not a live app",
        "platforms": ["fixture"],
        "gates": {name: {"status": "pass", "reason": "Synthetic claim for validator test",
                         "evidence": [{"procedure": "never executed", "artifact": "fixture",
                                       "observation": "synthetic claim"}]}
                  for name in schema["properties"]["gates"]["required"]},
    }


class ReportContractTests(unittest.TestCase):
    def test_schema_is_valid(self):
        Draft202012Validator.check_schema(json.loads(SCHEMA.read_text(encoding="utf-8")))

    def test_complete_claim_is_not_evidence_verification(self):
        result, code = validate_report(fixture())
        self.assertEqual(code, 0)
        self.assertTrue(result["result"]["claims_complete"])
        self.assertFalse(result["evidence_verified"])

    def test_pass_requires_evidence(self):
        report = fixture()
        report["gates"]["shared_substrate"]["evidence"] = []
        self.assertEqual(validate_report(report)[1], 2)

    def test_unknown_or_missing_gate_is_invalid(self):
        for mutation in ("unknown", "missing"):
            report = fixture()
            if mutation == "unknown":
                report["gates"]["mystery"] = report["gates"]["discoverability"]
            else:
                del report["gates"]["authority_and_safety"]
            self.assertEqual(validate_report(report)[1], 2)

    def test_unverified_and_failed_are_incomplete(self):
        for status in ("unverified", "fail"):
            report = fixture()
            report["gates"]["authority_and_safety"]["status"] = status
            result, code = validate_report(report)
            self.assertEqual(code, 3)
            self.assertEqual(result["result"]["incomplete_gates"], ["authority_and_safety"])

    def test_not_applicable_needs_nonblank_reason(self):
        report = fixture()
        report["gates"]["human_accessibility"] = {
            "status": "not_applicable", "reason": "CLI-only scoped fixture", "evidence": []}
        self.assertEqual(validate_report(report)[1], 0)
        report["gates"]["human_accessibility"]["reason"] = "  "
        self.assertEqual(validate_report(report)[1], 2)

    def test_stdin_and_invalid_input_emit_only_json(self):
        for raw, expected in ((json.dumps(fixture()), 0), ("not json", 2), ("[]", 2)):
            output = io.StringIO()
            self.assertEqual(run(["-"], io.StringIO(raw), output), expected)
            self.assertFalse(json.loads(output.getvalue())["evidence_verified"])

    def test_usage_error_is_machine_readable(self):
        output = io.StringIO()
        self.assertEqual(run([], io.StringIO(), output), 2)
        self.assertEqual(json.loads(output.getvalue())["error"]["code"], "USAGE")

    def test_private_invalid_values_are_not_echoed(self):
        report = fixture()
        report["schema_version"] = "private-value-must-not-be-echoed"
        result, code = validate_report(report)
        self.assertEqual(code, 2)
        self.assertNotIn("private-value", json.dumps(result))

    def test_recorded_procedures_are_data_not_commands(self):
        report = fixture()
        report["gates"]["discoverability"]["evidence"][0]["procedure"] = "exit 99; never execute"
        self.assertEqual(validate_report(report)[1], 0)


if __name__ == "__main__":
    unittest.main()
