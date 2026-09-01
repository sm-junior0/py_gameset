$ErrorActionPreference = "Stop"

Write-Host "FarmQuest 3D setup"
Write-Host "This installs the Panda3D track, not the legacy Kivy track."

if (Test-Path ".venv3d") {
    Write-Host "Using existing .venv3d directory."
} else {
    Write-Host "Creating .venv3d with the active Python..."
    & python -m venv .venv3d
}

Write-Host "Upgrading pip tooling..."
& .\.venv3d\Scripts\python.exe -m pip install --upgrade pip setuptools wheel

Write-Host "Installing Panda3D dependencies from PyPI..."
& .\.venv3d\Scripts\python.exe -m pip install -r requirements-3d.txt --index-url https://pypi.org/simple

Write-Host ""
Write-Host "Setup complete. Start the game with:"
Write-Host "  .\.venv3d\Scripts\Activate.ps1"
Write-Host "  python main.py"
