# Run Summary

This folder is the clean handoff for the traffic-signal controller run.

## What matters

- The final checkpoint is [best_model.zip](best_model.zip).
-- The final evaluation (10 seeds) against the Fixed-Time baseline shows the DQN performed slightly worse in mean delay for this final model.
	- Baseline mean delay: 612,811.500
	- DQN mean delay: 624,092.000
	- Absolute delta: +11,280.500 (worse by 1.841%)
	- Max queue: baseline 114.300 → DQN 119.400 (+5.1)
	- Throughput: baseline 427.400 → DQN 426.700 (−0.164%)
	- Evaluation results saved to: `eval_logs/evaluations.peak.retrained.final.npz`

Notes: The earlier "tight retrain" run (short training) had a modest improvement; this final longer run did not improve mean delay. Consider inspecting logs and training curves for instability, or re-tuning exploration schedule and reward components before re-training.

## What the logs show

- The playback log shows the controller actively switching with pressure and starvation overrides when the queue built up.
- The TraCI log records repeated connection-closed errors from SUMO; keep that file if you want to debug the simulator link, but it is not part of the model result itself.

## What to upload

- [artifacts_bundle.zip](artifacts_bundle.zip) if you want one file.
- Or upload the individual files if you want them visible separately in Google Drive.

## Artifact bundle

- Bundle SHA256: A8C00EB49AB7F7EEA750B2359622D550712F3554DE67134773BE6E4D68AF5226

## Small note

The learning curve is real, but it is sparse because the retrain only produced two evaluation checkpoints worth showing. That is fine here; it matches the short tight retrain we ran.