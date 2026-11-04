"""Build HEAD plus exactly one manifest batch, without staging or committing."""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import zipfile


def main():
    """Export committed files, overlay an explicit batch, and record isolated checks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = args.destination.resolve()
    if destination.exists() or destination.is_relative_to(root):
        raise SystemExit("Choose a new directory outside the working repository")
    manifest = json.loads((root / "docs/commits/staging-manifests.json").read_text(encoding="utf-8"))
    batch = next(b for b in manifest["batches"] if b["id"] == args.batch)
    if batch["dependencies"]:
        raise SystemExit("Later batches remain pending: commit and verify their prerequisites first; "
                         "record the resulting base HEAD before enabling their snapshot checks.")
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    archive = subprocess.check_output(["git", "archive", "--format=zip", "HEAD"], cwd=root)
    destination.mkdir(parents=True)
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        for name in zipped.namelist():
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or ":" in name or "\\" in name:
                raise SystemExit("Unsafe committed archive path")
        zipped.extractall(destination)
    hashes = {}
    for name in batch["files"]:
        source = (root / name).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            raise SystemExit(f"Invalid batch file: {name}")
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        hashes[name] = hashlib.sha256(target.read_bytes()).hexdigest()
    environment = os.environ.copy()
    for name in list(environment):
        if name.startswith(("PYTHONPATH", "DATABASE_URL", "TEST_DATABASE_URL", "MODEL_")):
            environment.pop(name)
    environment.update(AGENT_MODE="demo", EMBEDDING_MODE="lexical",
                       DATABASE_URL="sqlite:///./.local/batch.db", PYTHONUTF8="1")
    commands = [
        [sys.executable, "-m", "ruff", "check", "backend", "scripts", "tests"],
        [sys.executable, "-m", "pytest", "-q", "tests/unit/test_foundation.py"],
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        [sys.executable, "-m", "alembic", "check"],
    ]
    results = []
    for command in commands:
        result = subprocess.run(command, cwd=destination, env=environment,
                                capture_output=True, text=True, encoding="utf-8", errors="replace")
        results.append({"command": command, "exit_code": result.returncode,
                        "output": result.stdout + result.stderr})
        print(" ".join(command[1:]), "exit", result.returncode)
        print(result.stdout + result.stderr)
    evidence = {"base_commit": base, "batch": args.batch, "source_sha256": hashes,
                "results": results, "scope": "HEAD plus exactly this batch; no other uncommitted modules"}
    (destination / "batch-evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    raise SystemExit(1 if any(result["exit_code"] for result in results) else 0)


if __name__ == "__main__":
    main()
