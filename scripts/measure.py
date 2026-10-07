#!/usr/bin/env python3
"""Measure an explicitly supplied command; no scanner selected automatically."""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import resource
import signal
import subprocess
import sys
import time

def now():
    return datetime.now(timezone.utc).isoformat()

class Interrupted(Exception):
    pass

def interrupt(signum, frame):
    raise Interrupted(signum)

def stop_group(child):
    """Bound cleanup independently of whether the direct child has exited."""
    try:
        os.killpg(child.pid, signal.SIGTERM)
    except ProcessLookupError:
        child.wait()
        return
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        child.poll()
        try:
            os.killpg(child.pid, 0)
        except ProcessLookupError:
            break
        time.sleep(.02)
    try:
        os.killpg(child.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    child.wait()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--timeout", type=float, required=True)
    p.add_argument("--container", action="append", default=[],
                   help="Existing, explicitly named Docker container to sample")
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("command", nargs=argparse.REMAINDER)
    a = p.parse_args()
    cmd = a.command[1:] if a.command[:1] == ["--"] else a.command
    if not cmd or not math.isfinite(a.timeout) or a.timeout <= 0:
        p.error("Supply a command and a finite positive timeout.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,100}", a.run_id):
        p.error("Invalid run-id.")
    if any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", c) for c in a.container):
        p.error("Invalid container name.")
    os.umask(0o077)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=False)
    start_wall, start = now(), time.monotonic()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    events = [{"stage":"command","event":"start","timestamp":start_wall}]
    samples, status, rc = [], "completed", 0
    child = None
    previous_term = signal.signal(signal.SIGTERM, interrupt)
    try:
        # Raw streams may contain secrets: never copied into the publicable report.
        with (out/"stdout.raw.log").open("wb") as stdout, (out/"stderr.raw.log").open("wb") as stderr:
            child = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, start_new_session=True)
            next_sample = start
            while child.poll() is None:
                elapsed = time.monotonic()-start
                if elapsed >= a.timeout:
                    status, rc = "partial", 124
                    events.append({"stage":"command","event":"timeout","timestamp":now()})
                    break
                if a.container and time.monotonic() >= next_sample:
                    remaining = a.timeout - elapsed
                    try:
                        stats = subprocess.run(["docker","stats","--no-stream","--format","{{json .}}",*a.container],
                                               capture_output=True,text=True,timeout=min(2, remaining))
                        if stats.returncode:
                            samples.append({"timestamp":now(),"available":False,"reason":"docker-stats-failed"})
                        else:
                            for line in stats.stdout.splitlines():
                                row = json.loads(line)
                                samples.append({"timestamp":now(),"available":True,
                                                "container":row.get("Name"),
                                                "cpu_percent":row.get("CPUPerc"),
                                                "memory_usage":row.get("MemUsage"),
                                                "memory_percent":row.get("MemPerc"),
                                                "network_io":row.get("NetIO"),
                                                "block_io":row.get("BlockIO"),
                                                "pids":row.get("PIDs")})
                    except (OSError,ValueError,subprocess.TimeoutExpired):
                        samples.append({"timestamp":now(),"available":False,"reason":"collector-unavailable"})
                    next_sample = time.monotonic()+1
                time.sleep(min(0.1, max(0.001, a.timeout-(time.monotonic()-start))))
            if status != "partial":
                rc = child.wait()
                status = "completed" if rc == 0 else "failed"
    except KeyboardInterrupt:
        rc, status = 130, "partial"
    except Interrupted as interrupted:
        rc, status = 128 + interrupted.args[0], "partial"
        events.append({"stage":"command","event":"interrupted","timestamp":now()})
    except OSError:
        rc, status = 127, "blocked"
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        previous_int = signal.signal(signal.SIGINT, signal.SIG_IGN)
        if child is not None and (status == "partial" or child.poll() is None):
            stop_group(child)
        duration = time.monotonic()-start
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        events.append({"stage":"command","event":"finish","timestamp":now(),"status":status,"exit_code":rc})
        data = {"run_id":a.run_id,"status":status,"exit_code":rc,"duration_seconds":round(duration,6),
                "started_at":start_wall,"finished_at":now(),"synthetic":a.synthetic,
                "events":events,"metric_samples":samples,
                "measurement":{"local_children_user_cpu_seconds":after.ru_utime-before.ru_utime,
                               "local_children_system_cpu_seconds":after.ru_stime-before.ru_stime,
                               "local_children_peak_rss_bytes":after.ru_maxrss*(1 if sys.platform=="darwin" else 1024),
                               "scope":"Local child processes, including collector. Docker workload resources require container samples.",
                               "container_sampling":"docker stats, approximately 1s plus collector overhead" if a.container else "not-collected",
                               "target_telemetry":"not-collected","cost":"not-estimated",
                               "cleanup":"Host process group terminated on timeout/SIGINT/SIGTERM. SIGKILL and detached/remote containers require external cleanup."}}
        (out/"execution.json").write_text(json.dumps(data,indent=2))
        (out/"events.jsonl").write_text("".join(json.dumps(e)+"\n" for e in events))
        (out/"metrics-series.jsonl").write_text("".join(json.dumps(s)+"\n" for s in samples))
        signal.signal(signal.SIGTERM, previous_term)
        signal.signal(signal.SIGINT, previous_int)
    print(json.dumps({"run_id":a.run_id,"status":status,"exit_code":rc,"directory":str(out)}))
    return rc if 0 <= rc <= 255 else 1

if __name__ == "__main__":
    sys.exit(main())
