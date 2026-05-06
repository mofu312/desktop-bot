$ErrorActionPreference = "Stop"
$logFile = "D:\ccwork\Resona-Desktop-Pet\install_log.txt"
$venvDir = "D:\ccwork\Resona-Desktop-Pet\venv"
$reqFile = "D:\ccwork\Resona-Desktop-Pet\requirements.txt"
$targetDir = "$venvDir\Lib\site-packages"

# Step 1: Create venv (without pip to avoid issues)
Write-Output "=== Creating venv ==="
python -m venv $venvDir --clear --without-pip

# Step 2: Use system pip to install into venv
Write-Output "=== Installing requirements directly into venv ==="
pip install -r $reqFile --target $targetDir --no-input --verbose

Write-Output "=== INSTALLATION COMPLETE ==="
Write-Output "EXIT_CODE: $LASTEXITCODE"
