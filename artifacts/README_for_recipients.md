Recipient instructions — verify and run the release artifacts

- Verify checksum (PowerShell):

  Get-FileHash artifacts\artifacts_bundle.zip -Algorithm SHA256

  Compare the printed Hash with the contents of `artifacts\artifacts_bundle.sha256`.

- Contents included:
  - `artifacts/artifacts_bundle.zip` — curated bundle (models, logs, plots)
  - `artifacts/best_model.zip` — trained DQN model
  - `artifacts/learning_curve.png` — training curve
  - `eval_logs/evaluations.peak.retrained.extended.npz` — evaluation results
  - `artifacts/training_metadata.json` — provenance + hyperparameters

- Quick playback (requires SUMO + Python venv):

  1. Activate the venv: `\.venv\Scripts\Activate.ps1` (PowerShell)
  2. Run playback: `python scripts\playback_best_model.py --model artifacts\best_model.zip --gui`

- Re-run evaluation (example):

  python src\agent\evaluate.py --profile peak --mean-interval 5.0 --burst-intensity 1.5 \
    --horizon 4000 --max-steps 1200 --seeds 10 20 30 40 50 60 70 80 90 100 \
    --output eval_logs\evaluations.peak.retrained.extended.npz

- Notes:
  - The repo was not a git repo on my host, so `git_ref` in `training_metadata.json` may be empty.
  - Uploading the bundle to a remote store (GitHub release, cloud storage) requires your credentials.
