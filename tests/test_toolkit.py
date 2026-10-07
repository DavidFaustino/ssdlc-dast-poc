import importlib.util
import json
import subprocess
import sys
import tempfile
import os
import signal
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "poc.py"
MEASURE = ROOT / "scripts" / "measure.py"


class ToolkitTests(unittest.TestCase):
    def invoke(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True)

    def config(self):
        return dict(profile="test-profile", expected_account_id="123456789012",
                    region="us-east-1", vpc_id="vpc-12345678", subnet_id="subnet-12345678",
                    instance_type="m6i.xlarge", ami_id="ami-12345678",
                    owner="operator", expires_on="2026-10-10", report_retention_days=30,
                    egress_rules=[dict(cidr="10.1.0.0/16", from_port=443, to_port=443)])

    def test_help_does_not_require_aws(self):
        result = self.invoke("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preflight", result.stdout)

    def test_tfvars_preserves_account_and_rejects_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp)/"config.json", Path(tmp)/"vars.json"
            src.write_text(json.dumps(self.config()))
            result = self.invoke("tfvars", "--config", src, "--out", dst)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(dst.read_text())["expected_account_id"], "123456789012")
            self.assertNotEqual(self.invoke("tfvars", "--config", src, "--out", dst).returncode, 0)

    def test_unknown_secret_field_rejected_without_printing_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)/"config.json"
            src.write_text(json.dumps(dict(self.config(), token="sensitive-test-value")))
            result = self.invoke("tfvars", "--config", src, "--out", Path(tmp)/"out")
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("sensitive-test-value", result.stderr + result.stdout)

    def test_invalid_account_and_empty_egress_rejected(self):
        for change in [{"expected_account_id": "default"}, {"egress_rules": []}]:
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                src = Path(tmp)/"config.json"
                src.write_text(json.dumps(dict(self.config(), **change)))
                self.assertNotEqual(self.invoke("tfvars", "--config", src, "--out", Path(tmp)/"out").returncode, 0)

    def test_invalid_config_values_are_not_echoed(self):
        sentinel = "private-sentinel-value"
        for change in [{"expires_on":sentinel}, {"egress_rules":[dict(cidr=sentinel,from_port=443,to_port=443)]}]:
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                src = Path(tmp)/"config.json"
                src.write_text(json.dumps(dict(self.config(), **change)))
                result = self.invoke("tfvars", "--config", src, "--out", Path(tmp)/"out")
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn(sentinel, result.stdout + result.stderr)

    def test_identity_mismatch_stops_preflight(self):
        if not SCRIPT.exists():
            self.fail("preflight implementation missing")
        spec = importlib.util.spec_from_file_location("poc", SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        calls = []
        def fake(args, env=None):
            calls.append(args)
            return {"Account": "999999999999", "Arn": "arn:aws:iam::999999999999:role/test"}
        with self.assertRaises(ValueError):
            mod.preflight(self.config(), fake)
        self.assertEqual(len(calls), 1)

    def test_report_escapes_markup_and_detects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp)/"run.json", Path(tmp)/"report"
            src.write_text(json.dumps({"run_id":"test", "status":"failed",
                                      "exit_code":7, "duration_seconds":1,
                                      "label":"<script>alert(1)</script>", "synthetic":True}))
            result = self.invoke("report", "--input", src, "--out", out)
            self.assertEqual(result.returncode, 0, result.stderr)
            body = (out/"index.html").read_text()
            self.assertNotIn("<script>", body)
            self.assertIn("&lt;script&gt;", body)
            self.assertIn("failed", body)
            self.assertEqual(self.invoke("verify", "--directory", out).returncode, 0)
            (out/"index.html").write_text("tampered")
            self.assertNotEqual(self.invoke("verify", "--directory", out).returncode, 0)

    def test_measure_failure_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/"run"
            result = subprocess.run([sys.executable, str(MEASURE), "--out", str(out),
                                     "--run-id", "test", "--timeout", "10", "--",
                                     sys.executable, "-c", "raise SystemExit(7)"], capture_output=True)
            self.assertTrue((out/"execution.json").exists(), result.stderr)
            data = json.loads((out/"execution.json").read_text())
            self.assertEqual(data["exit_code"], 7)
            self.assertEqual(data["status"], "failed")
            self.assertEqual(result.returncode, 7)

    def test_measure_timeout_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/"run"
            result = subprocess.run([sys.executable, str(MEASURE), "--out", str(out),
                                     "--run-id", "test", "--timeout", "0.1", "--",
                                     sys.executable, "-c", "import time; time.sleep(5)"], capture_output=True)
            self.assertTrue((out/"execution.json").exists(), result.stderr)
            self.assertEqual(json.loads((out/"execution.json").read_text())["status"], "partial")
            self.assertEqual(result.returncode, 124)

    def test_timeout_kills_descendant_ignoring_sigterm(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, pidfile = Path(tmp)/"run", Path(tmp)/"child.pid"
            child_code = "import os,signal,time,pathlib;signal.signal(signal.SIGTERM,signal.SIG_IGN);pathlib.Path(" + repr(str(pidfile)) + ").write_text(str(os.getpid()));time.sleep(30)"
            parent_code = "import subprocess,sys,time;subprocess.Popen([sys.executable,'-c'," + repr(child_code) + "]);time.sleep(30)"
            result = subprocess.run([sys.executable, str(MEASURE), "--out", str(out),
                                     "--run-id", "test", "--timeout", "1", "--",
                                     sys.executable, "-c", parent_code], capture_output=True, timeout=10)
            self.assertTrue(pidfile.exists())
            pid = int(pidfile.read_text())
            try:
                stat = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
                self.assertTrue(not stat or stat.startswith("Z"), "descendant still running")
                self.assertEqual(result.returncode, 124)
            finally:
                try: os.kill(pid, signal.SIGKILL)
                except ProcessLookupError: pass

    def test_sigterm_writes_partial_evidence_and_stops_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, pidfile = Path(tmp)/"run", Path(tmp)/"child.pid"
            code = "import os,time,pathlib;pathlib.Path(" + repr(str(pidfile)) + ").write_text(str(os.getpid()));time.sleep(30)"
            process = subprocess.Popen([sys.executable, str(MEASURE), "--out", str(out),
                                        "--run-id", "test", "--timeout", "30", "--",
                                        sys.executable, "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            deadline = time.monotonic()+3
            while not pidfile.exists() and time.monotonic() < deadline: time.sleep(.02)
            self.assertTrue(pidfile.exists())
            pid = int(pidfile.read_text())
            try:
                process.terminate()
                process.communicate(timeout=7)
                self.assertTrue((out/"execution.json").exists(), "interruption evidence missing")
                self.assertEqual(json.loads((out/"execution.json").read_text())["status"], "partial")
                self.assertEqual(process.returncode, 143)
                stat = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
                self.assertTrue(not stat or stat.startswith("Z"), "child still running")
            finally:
                try: os.kill(pid, signal.SIGKILL)
                except ProcessLookupError: pass
                if process.poll() is None: process.kill()


if __name__ == "__main__":
    unittest.main()
