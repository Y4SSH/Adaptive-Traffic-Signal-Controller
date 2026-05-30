param(
    [string]$timesteps = '100000'
)

$env:TRAIN_TOTAL_TIMESTEPS = $timesteps
$env:PYTHONPATH = (Get-Location).Path
$python = Join-Path (Get-Location) '.venv310\Scripts\python.exe'
Write-Output "Starting full training with timesteps=$timesteps using python: $python"
Start-Process -FilePath $python -ArgumentList '.\src\agent\train.py' -RedirectStandardOutput '.\full_training.log' -RedirectStandardError '.\full_training.err' -NoNewWindow -PassThru
