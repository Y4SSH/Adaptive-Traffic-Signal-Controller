$env:TRAIN_TOTAL_TIMESTEPS='10'
$env:PYTHONPATH=(Get-Location).Path
$python = Join-Path (Get-Location) '.venv310\Scripts\python.exe'
Write-Output "Using python at $python"
if (-not (Test-Path $python)) { Write-Error "Python not found at $python"; exit 2 }
& $python '.\src\agent\train.py' 2>&1 | Tee-Object -FilePath '.\quick_train_output.log'