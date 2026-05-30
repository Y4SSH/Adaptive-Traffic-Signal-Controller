while ($true) {
  $i = Get-Item .\train_run_longer.log -ErrorAction SilentlyContinue
  if ($i -ne $null) {
    Write-Output "$(Get-Date) size=$($i.Length)"
    Get-Content .\train_run_longer.log -Tail 20 -Encoding UTF8
  } else {
    Write-Output "$(Get-Date) log missing"
  }
  Start-Sleep -Seconds 120
}
