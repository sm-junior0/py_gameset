$ErrorActionPreference = "Stop"

Write-Host "FarmQuest legacy Kivy setup"
Write-Host "For the new Panda3D direction, use .\scripts\setup_3d_windows.ps1"
Write-Host ""
Write-Host "Checking for Python 3.11..."

$python311Available = $false
try {
    $versionOutput = & py -3.11 --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $python311Available = $true
        Write-Host "Found $versionOutput"
    }
} catch {
    $python311Available = $false
}

if (-not $python311Available) {
    Write-Host ""
    Write-Host "Python 3.11 is required for this Kivy prototype."
    Write-Host "Install it from https://www.python.org/downloads/release/python-3119/"
    Write-Host "During install, enable 'Add python.exe to PATH' and keep the Python Launcher option enabled."
    Write-Host ""
    Write-Host "After installing, close and reopen PowerShell, then run:"
    Write-Host "  .\scripts\setup_windows.ps1"
    exit 1
}

if (Test-Path ".venv") {
    Write-Host "Using existing .venv directory."
} else {
    Write-Host "Creating .venv with Python 3.11..."
    & py -3.11 -m venv .venv
}

Write-Host "Upgrading pip tooling..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel

Write-Host "Installing FarmQuest dependencies..."
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete. Start the game with:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python main.py"
