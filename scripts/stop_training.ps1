$matches = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*train.py*' }
if ($matches) {
    foreach ($m in $matches) {
        Write-Output "Killing process $($m.ProcessId)"
        Stop-Process -Id $m.ProcessId -Force
    }
} else {
    Write-Output "No matching train.py processes found"
}

Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*train.py*' } | Select-Object ProcessId, CommandLine
