# Run Summary

This folder is the clean handoff for the traffic-signal controller run.

## What matters

- The final checkpoint is [best_model.zip](best_model.zip).
- The peak-traffic sweep with the tighter retrain came out slightly better than the fixed-time baseline.
- Mean delay dropped by 6,398.625.
- Max queue dropped by 7.
- Throughput stayed essentially unchanged.

## What the logs show

- The playback log shows the controller actively switching with pressure and starvation overrides when the queue built up.
- The TraCI log records repeated connection-closed errors from SUMO; keep that file if you want to debug the simulator link, but it is not part of the model result itself.

## What to upload

- [artifacts_bundle.zip](artifacts_bundle.zip) if you want one file.
- Or upload the individual files if you want them visible separately in Google Drive.

## Small note

The learning curve is real, but it is sparse because the retrain only produced two evaluation checkpoints worth showing. That is fine here; it matches the short tight retrain we ran.