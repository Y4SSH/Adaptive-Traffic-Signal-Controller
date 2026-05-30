$repoRoot = (Resolve-Path "$PSScriptRoot\.." ).Path
$activate = Join-Path $repoRoot ".venv310\Scripts\Activate.ps1"
if (Test-Path $activate) { . $activate } else { Write-Output "Venv activate not found at $activate" }

$checkFiles = @(
    "$repoRoot\best_model.zip",
    "$repoRoot\models\best_model.zip",
    "$repoRoot\final_model.zip",
    "$repoRoot\best_model\best_model.zip"
)

$train_timesteps = $env:TRAIN_TOTAL_TIMESTEPS
if (-not $train_timesteps) { $train_timesteps = "100000" }

Write-Output "Monitor started; will start full training with TRAIN_TOTAL_TIMESTEPS=$train_timesteps once a smoke model is detected."

while ($true) {
    foreach ($f in $checkFiles) {
        if (Test-Path $f) {
            Write-Output "Detected existing model: $f"
            Start-Sleep -Seconds 1
            $env:TRAIN_TOTAL_TIMESTEPS = $train_timesteps
            Set-Location $repoRoot
            Write-Output "Starting full training (this may take a long time). Output -> full_training.log"
            python .\src\agent\train.py 2>&1 | Tee-Object -FilePath "$repoRoot\full_training.log"
            Write-Output "Full training process exited.";
            exit
        }
    }
    Start-Sleep -Seconds 10
}
