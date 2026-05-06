$ErrorActionPreference = "Stop"
$projectRoot = "D:\ccwork\Resona-Desktop-Pet"
Set-Location $projectRoot

Write-Host "[Resona] Launching application..."
Write-Host "[Resona] Timestamp: $(Get-Date -Format 'HH:mm:ss')"

# Capture both stdout and stderr
$logFile = Join-Path $projectRoot "crash_ps.log"
$process = Start-Process -FilePath (Join-Path $projectRoot "venv\Scripts\python.exe") `
    -ArgumentList "main.py" `
    -WorkingDirectory $projectRoot `
    -NoNewWindow:$false `
    -PassThru `
    -RedirectStandardError $logFile

Write-Host "[Resona] PID: $($process.Id)"
Write-Host "[Resona] Waiting for process..."

# Wait up to 20 seconds
$process.WaitForExit(20000) | Out-Null

Write-Host "[Resona] Exit code: $($process.ExitCode)"
Write-Host "[Resona] ===== STDERR LOG ====="
if (Test-Path $logFile) {
    Get-Content $logFile
} else {
    Write-Host "(no stderr log file)"
}
Write-Host "[Resona] ===== END ====="

Read-Host -Prompt "Press Enter to close"
