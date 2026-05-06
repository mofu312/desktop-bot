$ErrorActionPreference = "Continue"
$reqFile = "D:\ccwork\Resona-Desktop-Pet\requirements.txt"
$logFile = "D:\ccwork\Resona-Desktop-Pet\install_system_log.txt"

# Kill any hanging Python processes
Get-Process -Name "python*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Output "=== Installing requirements (system Python) ==="
pip install -r $reqFile --no-input --verbose 2>&1 | Tee-Object -FilePath $logFile

Write-Output "=== INSTALLATION COMPLETE ==="
Write-Output "EXIT_CODE: $LASTEXITCODE"
