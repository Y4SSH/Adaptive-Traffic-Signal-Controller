# Evaluation & Training Report

Date: 2026-05-28

## Summary

- **Models**: [best_model.zip](best_model.zip) (exists), [final_model.zip](final_model.zip) (exists)
- **Learning curve**: [learning_curve.png](learning_curve.png)
- **Evaluation snapshot**: [eval_logs/evaluations.npz](eval_logs/evaluations.npz)

## Evaluation Metrics (from evaluations.npz)

- **Timesteps:** [5000]
- **Episode rewards (results):** [-731.0, -731.0, -731.0] (mean -731.0)
- **Episode lengths:** [536, 536, 536] (mean 536.0)

## Peak Profile Sweep

- **Run:** `src/agent/evaluate.py --profile peak --mean-interval 5.0 --burst-intensity 1.5 --horizon 3000 --max-steps 1200 --seeds 10 20 30 40 50 60 70 80`
- **Saved output:** [eval_logs/evaluations.peak.npz](eval_logs/evaluations.peak.npz)
- **Baseline mean delay:** 17,210,381.125
- **DQN mean delay:** 18,025,197.500
- **Baseline mean max queue:** 103.250
- **DQN mean max queue:** 103.125
- **Baseline mean throughput:** 379.000
- **DQN mean throughput:** 376.375

## Retrained Peak Sweep

- **Run:** `src/agent/evaluate.py --profile peak --mean-interval 5.0 --burst-intensity 1.5 --horizon 3000 --max-steps 1200 --seeds 10 20 30 40 50 60 70 80`
- **Saved output:** [eval_logs/evaluations.peak.retrained.npz](eval_logs/evaluations.peak.retrained.npz)
- **Baseline mean delay:** 14,498,090.375
- **DQN mean delay:** 10,355,397.875
- **Baseline mean max queue:** 102.250
- **DQN mean max queue:** 100.625
- **Baseline mean throughput:** 403.000
- **DQN mean throughput:** 443.750
- **Outcome:** retrained DQN outperformed the fixed-time baseline on peak traffic across all three core metrics.

## Handoff Notes

- The capped peak evaluation completed successfully after reducing per-episode max steps to 1200.
- Peak traffic is intentionally heavier and less stable than the default route set, so the delay metric is expected to be much larger than the baseline run in the summary above.
- The current policy remains usable for demos and regression checks, but the peak sweep does not yet show a clear performance edge over the fixed-time baseline.
- The retrained policy closes that gap: the latest peak sweep now beats the fixed-time baseline on delay, queue, and throughput.

## Train log excerpt (tail)

[See full log file](train_run_full.log)

```
[AdvancedTrafficEnv] setRedYellowGreenState used for phase 0
[AdvancedTrafficEnv] step 2620: action=0 phase_changed=False reward=-1.0
[AdvancedTrafficEnv] starvation override: lane=east_in_1 -> forcing phase 4 (was 0)
[AdvancedTrafficEnv] step 2628: action=0 phase_changed=True reward=-5.0
[AdvancedTrafficEnv] starvation override: lane=south_in_1 -> forcing phase 0 (was 0)
```

## Notes

- The evaluation used `best_model.zip` and produced consistent rewards across the small evaluation set saved in `eval_logs/evaluations.npz`.
- No new SUMO/TraCI "peer shutdown" errors were observed in recent log tail during the evaluation run.
- `learning_curve.png` is available and shows training progress (see file link above).

## Recommendations / Next Steps

- If you want to keep iterating: try a longer peak sweep with more seeds and per-seed traces to confirm the improvement is stable.
- If you want a conservative operating mode: compare the current calm thresholds against a slightly stricter starvation policy.
- I can generate a PDF report with embedded plots, or produce aggregated plots (per-seed reward traces + smoothed learning curve).

---

Report generated automatically. Files referenced above are in the workspace root.
