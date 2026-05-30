#!/usr/bin/env python3
"""Watch for a newly-written artifacts/best_model.zip and finish the release.

Usage: python scripts/finish_release_on_model_ready.py --start-time <ISO> [--timesteps 100000]
"""
import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def run(cmd, check=True, capture=False):
    print(f"RUN: {cmd}")
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    return subprocess.run(cmd, check=check, capture_output=capture, text=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start-time", required=True)
    p.add_argument("--timesteps", type=int, default=100000)
    p.add_argument("--eval-output", default="eval_logs/evaluations.peak.retrained.final.npz")
    p.add_argument("--eval-seeds", nargs="*", default=["10","20","30","40","50","60","70","80","90","100"])
    args = p.parse_args()

    start_time = datetime.fromisoformat(args.start_time)
    repo_root = Path(__file__).resolve().parents[1]
    model_path = repo_root / "artifacts" / "best_model.zip"

    print(f"Monitor start time: {start_time.isoformat()}")
    print(f"Waiting for model at: {model_path}")

    # Wait until best_model.zip is created/modified after start_time
    start_ts = start_time.timestamp()
    while True:
        if model_path.exists():
            mtime_ts = model_path.stat().st_mtime
            mtime = datetime.fromtimestamp(mtime_ts)
            print(f"Found model mtime={mtime.isoformat()}")
            if mtime_ts > start_ts:
                print("Detected new model. Proceeding with finalization steps.")
                break
        time.sleep(30)

    # 1) Run evaluation (multi-seed)
    eval_cmd = [
        sys.executable, str(repo_root / "src" / "agent" / "evaluate.py"),
        "--profile", "peak",
        "--mean-interval", "5.0",
        "--burst-intensity", "1.5",
        "--horizon", "4000",
        "--max-steps", "1200",
        "--output", args.eval_output,
    ] + ["--seeds"] + list(args.eval_seeds)

    try:
        run(eval_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("Evaluation failed:", e)

    # 2) Package artifacts into artifacts/artifacts_bundle.zip
    bundle_path = repo_root / "artifacts" / "artifacts_bundle.zip"
    if bundle_path.exists():
        bundle_path.unlink()
    # Use shutil.make_archive to create zip from artifacts directory
    archive_base = str(repo_root / "artifacts" / "artifacts_bundle")
    print("Creating zip bundle...")
    shutil.make_archive(archive_base, 'zip', root_dir=str(repo_root / "artifacts"))

    # 3) Compute SHA256
    sha = sha256_file(bundle_path)
    print(f"Bundle SHA256: {sha}")
    sha_file = repo_root / "artifacts" / "artifacts_bundle.sha256"
    sha_file.write_text(sha + "\n")

    # 4) Update training_metadata.json
    meta_path = repo_root / "artifacts" / "training_metadata.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
    else:
        meta = {}

    meta.setdefault("training", {})["total_timesteps"] = args.timesteps
    meta.setdefault("artifacts", {}).setdefault("bundle", {})["sha256"] = sha
    meta.setdefault("evaluation_results", {})["path"] = args.eval_output
    meta.setdefault("provenance", {})["created_at"] = datetime.now().isoformat()

    # try to get git ref
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
        meta.setdefault("provenance", {})["git_ref"] = out
    except Exception:
        meta.setdefault("provenance", {})["git_ref"] = meta.get("provenance", {}).get("git_ref", "")

    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"Updated metadata at {meta_path}")

    # 5) Commit, tag, and push
    try:
        run(["git", "add", "artifacts/training_metadata.json", "artifacts/artifacts_bundle.sha256", str(bundle_path), args.eval_output])
        run(["git", "commit", "-m", "Finalize release: final model, evaluation, and bundle"], check=False)
        run(["git", "tag", "-a", "v1.0-final", "-m", "Final model release"])
        run(["git", "push", "origin", "--follow-tags"], check=False)
        print("Committed and pushed final artifacts (tags included).")
    except Exception as e:
        print("Git commit/push failed:", e)

    # 6) Optionally upload to GitHub release if gh CLI is available and authenticated
    try:
        # create or ensure release exists
        run(["gh", "release", "view", "v1.0-final"], check=False)
        run(["gh", "release", "create", "v1.0-final", "--title", "v1.0-final", "--notes", "Final release with trained model and evaluation"], check=False)
        run(["gh", "release", "upload", "v1.0-final", str(bundle_path)], check=False)
        print("Attempted to upload bundle to GitHub release v1.0-final (if authenticated).")
    except Exception as e:
        print("GitHub upload skipped or failed:", e)

    print("Finish-release script completed.")


if __name__ == "__main__":
    main()
