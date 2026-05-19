# Run this file in Windows PowerShell as Administrator after a PC reset.
# It enables WSL 2 features and starts Docker Desktop after reboot.

$ErrorActionPreference = "Stop"

Write-Host "Enabling WSL and Virtual Machine Platform..."
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

Write-Host "Setting WSL default version to 2..."
wsl --set-default-version 2

Write-Host "Installing Ubuntu 24.04..."
wsl --install -d Ubuntu-24.04

Write-Host "WSL setup command finished. Reboot Windows if prompted, then open Docker Desktop."
