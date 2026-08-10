"""Disposable Docker sandbox for untrusted, deliberately-cheating model code.

Prime Directives §0.4 / §5 (non-negotiable):
  * disposable container, removed after every run
  * NO network egress                (--network none)
  * NO host bind-mounts               (files move by `docker cp`, never `-v`)
  * NO credentials / secrets in env   (clean env; only an explicit allowlist is forwarded)
  * full write access INSIDE the container (the realistic condition — agents may edit tests)
Containment is by disposability + no-net + no-mounts, NOT by a read-only fs.

DoD (WS2): run one command on one task fully isolated and capture a valid result.
Run `python sandbox_runner.py --smoke` to PROVE isolation on python:3.11-slim.

Pure stdlib + the `docker` CLI. No pip deps.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


class SandboxError(RuntimeError):
    pass


def _run(cmd: List[str], timeout: Optional[float] = None) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def _daemon_up() -> bool:
    """True iff the `docker` CLI exists AND the daemon answers. Both are hard prerequisites."""
    try:
        rc, _, _ = _run(["docker", "info"])
    except OSError:
        return False
    return rc == 0


def image_digest(image: str) -> str:
    """Pinned digest for the image (Prime Directive §6). Empty string if none locally.

    Returns "" rather than raising when docker is absent, so provenance capture degrades to
    "digest unrecorded" instead of taking down the caller.
    """
    if not _daemon_up():
        return ""
    rc, out, _ = _run(["docker", "image", "inspect", "--format", "{{index .RepoDigests 0}}", image])
    if rc == 0 and out.strip() and out.strip() != "<no value>":
        return out.strip()
    rc, out, _ = _run(["docker", "image", "inspect", "--format", "{{.Id}}", image])
    return out.strip() if rc == 0 else ""


@dataclass
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_s: float
    image: str
    image_digest: str
    network_disabled: bool = True
    mounts: List[str] = field(default_factory=list)   # always [] — asserted below
    timed_out: bool = False

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def run_in_sandbox(
    image: str,
    command: str,
    copy_in: Optional[Dict[str, str]] = None,     # host_path -> container_path
    copy_out: Optional[Dict[str, str]] = None,    # container_path -> host_path
    workdir: str = "/work",
    timeout_s: float = 900.0,
    env_allowlist: Optional[Dict[str, str]] = None,
    memory: str = "2g",
    cpus: str = "2.0",
    pids_limit: int = 512,
) -> SandboxResult:
    """Execute `command` in a throwaway container with no net, no mounts, clean env."""
    if not _daemon_up():
        raise SandboxError(
            "Docker is a hard prerequisite and is not available (the `docker` CLI is missing or "
            "the daemon is not answering `docker info`). Everything that executes candidate "
            "patches runs in a container by Prime Directive §0.4, so there is no host fallback. "
            "Install/start Docker and `docker pull python:3.11-slim`, then retry. "
            "See the Prerequisites section of README.md; `python tests/test_smoke.py` is the only "
            "docker-free entry point."
        )
    name = f"cuarzo-sbx-{uuid.uuid4().hex[:12]}"
    digest = image_digest(image)
    env_allowlist = env_allowlist or {}
    # Safety caps below are containment, not scale infra (§0.1): bound blast radius only.
    create = [
        "docker", "create", "--name", name,
        "--network", "none",          # no egress
        "--memory", memory, "--cpus", cpus, "--pids-limit", str(pids_limit),
        "--workdir", workdir,
    ]
    for k, v in env_allowlist.items():
        create += ["--env", f"{k}={v}"]
    create += [image, "sleep", str(int(timeout_s) + 60)]

    rc, _, err = _run(create)
    if rc != 0:
        raise SandboxError(f"docker create failed: {err.strip()}")

    started = time.time()
    timed_out = False
    try:
        rc, _, err = _run(["docker", "start", name])
        if rc != 0:
            raise SandboxError(f"docker start failed: {err.strip()}")

        _run(["docker", "exec", name, "mkdir", "-p", workdir])
        for host_path, cont_path in (copy_in or {}).items():
            rc, _, err = _run(["docker", "cp", host_path, f"{name}:{cont_path}"])
            if rc != 0:
                raise SandboxError(f"copy_in failed ({host_path}): {err.strip()}")

        # Run the untrusted command via a login-free shell inside the container.
        exec_cmd = ["docker", "exec", "--workdir", workdir, name, "sh", "-lc", command]
        try:
            code, out, cerr = _run(exec_cmd, timeout=timeout_s)
        except subprocess.TimeoutExpired as te:
            timed_out = True
            code, out, cerr = 124, te.stdout or "", (te.stderr or "") + "\n[sandbox] TIMEOUT"
            if isinstance(out, bytes):
                out = out.decode("utf-8", "replace")
            if isinstance(cerr, bytes):
                cerr = cerr.decode("utf-8", "replace")

        for cont_path, host_path in (copy_out or {}).items():
            os.makedirs(os.path.dirname(host_path) or ".", exist_ok=True)
            _run(["docker", "cp", f"{name}:{cont_path}", host_path])  # best-effort

        return SandboxResult(
            exit_code=code, stdout=out, stderr=cerr,
            duration_s=round(time.time() - started, 3),
            image=image, image_digest=digest,
            network_disabled=True, mounts=[], timed_out=timed_out,
        )
    finally:
        _run(["docker", "rm", "-f", name])   # disposable: always destroyed


def verify_isolation(image: str = "python:3.11-slim") -> dict:
    """PROVE the guarantees hold. Returns a report; raises if any guarantee is violated."""
    report = {"image": image, "image_digest": image_digest(image)}

    # 1. Network egress must FAIL.
    net_probe = ("python -c \"import socket,sys\n"
                 "try:\n socket.setdefaulttimeout(4); socket.create_connection(('1.1.1.1',53))\n"
                 " print('NET_OK'); sys.exit(0)\n"
                 "except Exception as e:\n print('NET_BLOCKED', e); sys.exit(7)\"")
    r = run_in_sandbox(image, net_probe, timeout_s=30)
    report["network_blocked"] = (r.exit_code != 0 and "NET_OK" not in r.stdout)
    report["network_probe_out"] = (r.stdout + r.stderr).strip()

    # 2. No host mounts: only expected pseudo/overlay filesystems present.
    mnt = run_in_sandbox(image, "cat /proc/mounts | awk '{print $2}' | sort -u", timeout_s=30)
    suspicious = [ln for ln in mnt.stdout.splitlines()
                  if ln.startswith(("/Users", "/home", "/host", "/mnt", "/media"))]
    report["host_mounts_found"] = suspicious
    report["no_host_mounts"] = (len(suspicious) == 0)

    # 3. In-container writes work (realistic condition — agent may edit tests).
    w = run_in_sandbox(image, "echo hi > /work/x && cat /work/x", timeout_s=30)
    report["writable_workdir"] = (w.exit_code == 0 and "hi" in w.stdout)

    # 4. Clean env: no HOST secrets forwarded in. Env vars DECLARED BY THE IMAGE ITSELF
    #    (e.g. the official python image bakes in GPG_KEY, the CPython signing key) are
    #    legitimate and must NOT be flagged. Only vars present beyond the image baseline
    #    that look secret-ish count as a host leak.
    rc, base_json, _ = _run(["docker", "image", "inspect", "--format", "{{json .Config.Env}}", image])
    image_env_names: set = set()
    if rc == 0 and base_json.strip():
        try:
            image_env_names = {kv.split("=", 1)[0] for kv in json.loads(base_json)}
        except json.JSONDecodeError:
            pass
    e = run_in_sandbox(image, "env", timeout_s=30)
    secret_hints = ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "AWS_", "ANTHROPIC", "OPENAI")
    leaked = [
        name for name in (ln.split("=", 1)[0] for ln in e.stdout.splitlines() if "=" in ln)
        if name not in image_env_names and any(h in name.upper() for h in secret_hints)
    ]
    report["image_env_baseline"] = sorted(image_env_names)
    report["leaked_env_vars"] = leaked
    report["clean_env"] = (len(leaked) == 0)

    report["all_guarantees_pass"] = all([
        report["network_blocked"], report["no_host_mounts"],
        report["writable_workdir"], report["clean_env"],
    ])
    if not report["all_guarantees_pass"]:
        raise SandboxError(f"isolation guarantees VIOLATED: {json.dumps(report, indent=2)}")
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Cuarzo disposable Docker sandbox")
    ap.add_argument("--smoke", action="store_true", help="prove isolation guarantees and exit")
    ap.add_argument("--image", default="python:3.11-slim")
    ap.add_argument("--cmd", help="run a single command in the sandbox and print the result")
    args = ap.parse_args()

    if not _daemon_up():
        print("ERROR: docker daemon not reachable", file=sys.stderr)
        sys.exit(2)

    if args.smoke:
        rep = verify_isolation(args.image)
        print(json.dumps(rep, indent=2))
        print("\nSANDBOX ISOLATION: OK  (no net, no host mounts, writable workdir, clean env)")
    elif args.cmd:
        res = run_in_sandbox(args.image, args.cmd)
        print(json.dumps(res.to_dict(), indent=2))
    else:
        ap.print_help()
