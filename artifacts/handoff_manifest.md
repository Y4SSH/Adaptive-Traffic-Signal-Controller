# Handoff Notes

This bundle is the clean handoff for the adaptive traffic signal controller. It contains the retrained model, the peak-traffic evaluation results, the learning curve, and the logs from the GUI playback run.

## What to keep

- [best_model.zip](../best_model.zip): the final retrained checkpoint that should be used for playback and any follow-up evaluation.
- [run_summary.md](../run_summary.md): the short plain-English note that explains the run without the raw log noise.
- [learning_curve.png](../learning_curve.png): the training curve for the retrained run.
- [eval_logs/evaluations.peak.retrained.tight.npz](../eval_logs/evaluations.peak.retrained.tight.npz): the peak-traffic comparison data for baseline vs DQN.
- [playback_terminal_output.txt](../playback_terminal_output.txt): the playback terminal output captured while the GUI was running.
- [sumo_traci_error.log](../sumo_traci_error.log): the TraCI error log with repeated connection-closed events.

## What is inside the bundle

- `best_model.zip`
- `best_model_copy.zip` was removed after the safe cleanup step and should not be re-uploaded.
- `artifacts_bundle.zip`: the curated archive for sharing; it should contain only the current deliverables, not the older backup archive.

## Practical commands

```powershell
& ".venv\Scripts\python.exe" scripts\playback_best_model.py --seed 42 --mean-interval 5.0 --profile peak --burst-intensity 1.5
& ".venv\Scripts\python.exe" src\agent\evaluate.py --profile peak --mean-interval 5.0 --burst-intensity 1.5 --horizon 3000 --max-steps 1200 --seeds 10 20 30 40 50 60 70 80 --output eval_logs\evaluations.peak.retrained.tight.npz
```

## Final status

- The retrained DQN is the preferred checkpoint for peak traffic.
- The peak sweep showed a small but real improvement over baseline in mean delay and max queue.
- The bundle is ready for upload or archival.