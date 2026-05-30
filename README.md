#  Adaptive Traffic Signal Controller Using Deep Reinforcement Learning (DQN)

A production-ready repository implementing a DQN-based traffic signal controller for SUMO using a custom Gym environment and Stable-Baselines3. The project includes training, multi-seed evaluation, demand generation, GUI playback, tests, and curated artifacts for handoff.

---

## System Architecture & Data Flow

The control loop runs at localized decision intervals (Δt ≈ 5s). High-level components:

- SUMO (simulator): vehicle physics and lane state.
- Gym environment: `src/env/traffic_env.py` — collects lane telemetry, builds observations, applies safety overrides.
- Agent: Stable-Baselines3 DQN (`src/agent/train.py`) — chooses phase-switch actions.
- Controller bridge: TraCI interface enforces yellow buffers and phase-change constraints.

```
SUMO -> Gym Env (observations) -> DQN Agent -> TraCI Controller -> SUMO
```

### Observation & Action

- Observations: halting counts, mean speeds, current phase index/time-in-phase, short-window queue statistics (see `src/env/traffic_env.py`).
- Actions: discrete phase choices with enforced yellow-phase transitions and control-interval timing.

## Evaluation Summary

Final 10-seed validation summary (saved to `eval_logs/evaluations.peak.retrained.final.npz`):

| Metric                | Baseline | DQN (final) | Delta |
|----------------------:|---------:|------------:|------:|
| Mean Delay (s)        | 612,811.5| 624,092.0   | +1.84% (worse)
| Max Queue (vehicles)  | 114.3    | 119.4       | +5.1
| Throughput (vehicles) | 427.4    | 426.7       | −0.16%

Note: an earlier short retrain produced a small improvement; the final longer run worsened mean delay — see `artifacts/learning_curve.png` and `artifacts/run_summary.md` for diagnostics.

## Quickstart

1. Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Train (example):

```bash
python src/agent/train.py --total-timesteps 100000
```

3. Evaluate (example):

```bash
python src/agent/evaluate.py --profile peak --mean-interval 5.0 --burst-intensity 1.5 \
  --horizon 4000 --max-steps 1200 --seeds 10 20 30 40 50 60 70 80 90 100 \
  --output eval_logs/evaluations.peak.retrained.final.npz
```

4. Playback (SUMO-GUI):

```bash
python scripts/playback_best_model.py --seed 42 --mean-interval 5.0 --profile peak --burst-intensity 1.5 --gui
```

5. Tests:

```bash
python -m pytest
```

## Robustness & Safety Overrides

- Starvation prevention: forces relief to lanes starved beyond `STARVATION_CYCLES`.
- Dynamic topology discovery: uses `traci.trafficlight.getControlledLinks()` to map lanes to phases reliably.

## Important Files

- `src/env/traffic_env.py` — environment and overrides
- `src/agent/train.py` — training script (DQN)
- `src/agent/evaluate.py` — evaluation harness
- `scripts/playback_best_model.py` — SUMO GUI playback
- `artifacts/` — `best_model.zip`, `learning_curve.png`, `artifacts_bundle.zip`, `training_metadata.json`, `artifacts_bundle.sha256`
- `eval_logs/` — evaluation outputs

---
