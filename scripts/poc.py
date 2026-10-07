#!/usr/bin/env python3
"""Preparation and reporting. No apply, destroy, deployment or scan command."""
import argparse
import hashlib
import html
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

FIELDS = {"profile", "expected_account_id", "region", "vpc_id", "subnet_id",
          "instance_type", "ami_id", "owner", "expires_on", "report_retention_days", "egress_rules"}
REPORT_FIELDS = {"run_id", "status", "exit_code", "duration_seconds", "label", "synthetic",
                 "started_at", "finished_at", "measurement", "findings", "coverage",
                 "cost_estimate", "application", "release", "commit", "digest", "environment",
                 "metric_samples", "events"}

def load_config(path):
    c = json.loads(Path(path).read_text())
    if not isinstance(c, dict) or set(c) != FIELDS:
        raise ValueError("Configuration requires exactly the documented fields; unknown fields rejected.")
    if not isinstance(c["expected_account_id"], str) or not re.fullmatch(r"[0-9]{12}", c["expected_account_id"]):
        raise ValueError("Invalid expected account ID.")
    for key in ("profile", "region", "instance_type", "owner"):
        if not isinstance(c[key], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.@/-]{0,100}", c[key]):
            raise ValueError("Invalid configuration identifier: " + key)
    for key, prefix in (("vpc_id","vpc"), ("subnet_id","subnet"), ("ami_id","ami")):
        if not isinstance(c[key], str) or not re.fullmatch(prefix + r"-[0-9a-f]{8,17}", c[key]):
            raise ValueError("Invalid resource identifier: " + key)
    from datetime import date
    try:
        date.fromisoformat(c["expires_on"])
    except (TypeError, ValueError):
        raise ValueError("Invalid expiration date; expected YYYY-MM-DD.") from None
    if type(c["report_retention_days"]) is not int or not 1 <= c["report_retention_days"] <= 3650:
        raise ValueError("Retention must be 1..3650 days.")
    if not isinstance(c["egress_rules"], list) or not c["egress_rules"]:
        raise ValueError("Explicit egress rules are required.")
    for rule in c["egress_rules"]:
        if not isinstance(rule, dict) or set(rule) != {"cidr","from_port","to_port"}:
            raise ValueError("Invalid egress rule fields.")
        if not isinstance(rule["cidr"], str):
            raise ValueError("Invalid egress CIDR type.")
        try:
            net = ipaddress.ip_network(rule["cidr"], strict=True)
        except ValueError:
            raise ValueError("Invalid egress CIDR.") from None
        if net.version != 4:
            raise ValueError("Only IPv4 egress supported by this module.")
        if any(type(rule[k]) is not int for k in ("from_port","to_port")) or not 1 <= rule["from_port"] <= rule["to_port"] <= 65535:
            raise ValueError("Invalid egress ports.")
    return c

def profile_env(profile):
    env = os.environ.copy()
    # Avoid accidental precedence from credentials/role injection in the shell.
    for key in ("AWS_ACCESS_KEY_ID","AWS_SECRET_ACCESS_KEY","AWS_SESSION_TOKEN",
                "AWS_SECURITY_TOKEN","AWS_ROLE_ARN","AWS_WEB_IDENTITY_TOKEN_FILE",
                "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI","AWS_CONTAINER_CREDENTIALS_FULL_URI",
                "AWS_DEFAULT_PROFILE"):
        env.pop(key, None)
    env.update(AWS_PROFILE=profile, AWS_PAGER="", AWS_EC2_METADATA_DISABLED="true")
    return env

def call_json(args, env=None):
    result = subprocess.run(args, capture_output=True, text=True, timeout=45, env=env)
    if result.returncode:
        raise ValueError("CLI request failed; check session, permissions and endpoint locally. Raw output withheld.")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise ValueError("CLI returned invalid JSON.") from None

def preflight(c, caller=call_json):
    base = ["aws", "--profile", c["profile"], "--region", c["region"], "--output", "json"]
    env = profile_env(c["profile"])
    identity = caller(base + ["sts", "get-caller-identity"], env=env)
    if identity.get("Account") != c["expected_account_id"]:
        raise ValueError("Account mismatch. Stopping before resource discovery.")
    data = caller(base + ["ec2", "describe-subnets", "--subnet-ids", c["subnet_id"]], env=env)
    subnets = data.get("Subnets", [])
    if len(subnets) != 1 or subnets[0].get("VpcId") != c["vpc_id"]:
        raise ValueError("Subnet does not belong to the expected VPC.")
    return {"status":"identity-and-subnet-verified", "account":identity["Account"],
            "region":c["region"], "subnet_id":c["subnet_id"], "vpc_id":c["vpc_id"],
            "tools":{t:bool(shutil.which(t)) for t in ("aws","terraform","docker","kubectl","argocd","gh")},
            "not_verified":["IAM provisioning permissions","target routes/DNS/TLS/authentication",
                            "SSM and package registry egress","AMI bootstrap compatibility","available capacity"]}

def write_new(path, body):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as stream:
        stream.write(body)

def reject_secrets(value):
    text = json.dumps(value)
    if re.search(r"(?i)bearer\s+\S+|github_pat_|ghp_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN .*PRIVATE KEY|eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", text):
        raise ValueError("Potential credential detected; report refused.")
    def walk(x):
        if isinstance(x, dict):
            for k,v in x.items():
                if re.search(r"(?i)password|authorization|cookie|secret|token|curl.command|raw.request|raw.response", k):
                    raise ValueError("Sensitive field prohibited in report.")
                walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(value)

def report(src, out):
    data = json.loads(Path(src).read_text())
    if not isinstance(data, dict) or set(data) - REPORT_FIELDS:
        raise ValueError("Unknown report fields; supply normalized data only.")
    if not isinstance(data.get("run_id"), str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,100}", data["run_id"]):
        raise ValueError("Invalid run_id.")
    if data.get("status") not in ("completed","failed","partial","blocked","inconclusive"):
        raise ValueError("Invalid execution status.")
    reject_secrets(data)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    label = "EXEMPLO SINTÉTICO — NÃO É RESULTADO DAST" if data.get("synthetic") else "EXECUÇÃO — REVISAR COBERTURA E EVIDÊNCIAS"
    sections = [
        ("Identidade e execução", {k:v for k,v in data.items() if k not in
          ("findings","measurement","coverage","cost_estimate","metric_samples","events")}),
        ("Segurança", data.get("findings", "Não importado — ausência de dados não significa zero achados.")),
        ("Cobertura", data.get("coverage", "Não coletada.")),
        ("Recursos e desempenho", data.get("measurement", "Não coletados.")),
        ("Amostras de métricas", data.get("metric_samples", "Não incluídas.")),
        ("Linha do tempo", data.get("events", "Não incluída.")),
        ("FinOps", data.get("cost_estimate", "Não estimado; requer região, preços e duração faturável."))
    ]
    parts = []
    for title, value in sections:
        parts.append("<section><h2>"+html.escape(title)+"</h2><pre>"+
                     html.escape(json.dumps(value, ensure_ascii=False, indent=2))+"</pre></section>")
    page = """<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>DAST — relatório de execução</title><style>
body{font:16px system-ui;max-width:1100px;margin:auto;padding:24px;color:#162333;background:#f5f7fa}
section{background:white;padding:16px;margin:16px 0;border:1px solid #d6dce4}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px}
h1{font-size:26px}h2{font-size:19px}.notice{padding:16px;background:#fff1cb}
</style><h1>Relatório de execução DAST</h1>"""
    page += "<p class=notice>"+label+"</p><p>Conclusão do processo não é aprovação de segurança. Dados ausentes não são zero.</p>"
    page += "".join(parts) + "</html>"
    write_new(out/"index.html", page)
    write_new(out/"execution.json", json.dumps(data, ensure_ascii=False, indent=2))
    entries = [{"path":f.name, "sha256":hashlib.sha256(f.read_bytes()).hexdigest(),
                "bytes":f.stat().st_size} for f in sorted(out.iterdir())]
    write_new(out/"manifest.json", json.dumps({"files":entries}, indent=2))
    return {"directory":str(out), "files":len(entries), "publication":"not-performed"}

def verify(directory):
    root = Path(directory).resolve()
    manifest = json.loads((root/"manifest.json").read_text())
    expected = {"manifest.json"}
    for entry in manifest["files"]:
        relative = Path(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe manifest path.")
        path = root / relative
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError("Unsafe or missing evidence file.")
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"] or path.stat().st_size != entry["bytes"]:
            raise ValueError("Evidence integrity mismatch.")
        expected.add(relative.as_posix())
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() or p.is_symlink()}
    if actual != expected:
        raise ValueError("Unexpected/unlisted evidence files.")
    return {"integrity":"verified", "authenticity":"not-proven-by-hash"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("tfvars","preflight"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--config", required=True)
        cmd.add_argument("--out", required=True)
    cmd = sub.add_parser("report")
    cmd.add_argument("--input", required=True)
    cmd.add_argument("--out", required=True)
    cmd = sub.add_parser("verify")
    cmd.add_argument("--directory", required=True)
    args = parser.parse_args()
    os.umask(0o077)
    try:
        if args.command in ("tfvars","preflight"):
            c = load_config(args.config)
            if args.command == "tfvars":
                result = dict(c)
                result["aws_profile"] = result.pop("profile")
            else:
                result = preflight(c)
            write_new(args.out, json.dumps(result, indent=2))
            print("Created local file; no resources created.")
        elif args.command == "report":
            print(json.dumps(report(args.input, args.out)))
        else:
            print(json.dumps(verify(args.directory)))
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        # Exceptions never include CLI stdout/stderr or configuration values.
        print("ERROR: "+str(exc), file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
