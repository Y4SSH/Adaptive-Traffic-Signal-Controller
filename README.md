# Adaptive Traffic Signal Controller

Adaptive traffic signal control for a SUMO intersection using Deep Q-Networks.

## What is included

- SUMO/TraCI environment in `src/env/traffic_env.py`
- DQN training in `src/agent/train.py`
- Multi-seed evaluation in `src/agent/evaluate.py`
- Demand generation in `configs/demand_generator.py`
- GUI playback in `scripts/playback_best_model.py`
- Smoke tests under `tests/`

## Setup

1. Install SUMO and set `SUMO_HOME` if it is not already available.
2. Install Python dependencies:

```powershell
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
```

## Train

```powershell
& ".venv\Scripts\python.exe" src\agent\train.py
```

Useful environment variables:

- `TRAIN_TOTAL_TIMESTEPS`: total training steps.
- `TRAIN_DEMAND_SEED`: seed for route generation.
- `SUMO_NET_PATH`: override the network file path.

Artifacts written by training:

- `best_model.zip`
- `final_model.zip`
- `learning_curve.png`
- `eval_logs/evaluations.npz`

## Evaluate

```powershell
& ".venv\Scripts\python.exe" src\agent\evaluate.py
```

Peak traffic evaluation is supported through CLI flags on the evaluation script.

## Playback

```powershell
& ".venv\Scripts\python.exe" scripts\playback_best_model.py --seed 42 --mean-interval 5.0 --profile peak --burst-intensity 1.5
```

## Tests

```powershell
& ".venv\Scripts\python.exe" -m pytest
```

The SUMO-backed smoke test skips automatically if SUMO is not available, so the suite can still run in CI.
