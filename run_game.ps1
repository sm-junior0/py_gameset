$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "No venv found. Creating one with the active Python..."
    python -m venv venv
}

Write-Host "Starting FarmQuest..."
& .\venv\Scripts\python.exe main.py
