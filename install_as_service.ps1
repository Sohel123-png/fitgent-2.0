# PowerShell script to install the authentication server as a Windows service
# This script requires administrative privileges to run

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "This script requires administrative privileges. Please run as administrator."
    exit
}

# Get the current directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = "python.exe"
$appPath = Join-Path $scriptPath "app.py"

# Create a new service using NSSM (Non-Sucking Service Manager)
# You need to download and install NSSM first: https://nssm.cc/download
$nssmPath = "C:\path\to\nssm.exe" # Update this path to where you installed NSSM

# Check if NSSM exists
if (-not (Test-Path $nssmPath)) {
    Write-Host "NSSM not found at $nssmPath. Please download and install NSSM first."
    Write-Host "Download from: https://nssm.cc/download"
    exit
}

# Install the service
& $nssmPath install "AuthenticationServer" $pythonPath $appPath
& $nssmPath set "AuthenticationServer" DisplayName "Authentication Server"
& $nssmPath set "AuthenticationServer" Description "Flask Authentication Server"
& $nssmPath set "AuthenticationServer" AppDirectory $scriptPath
& $nssmPath set "AuthenticationServer" Start SERVICE_AUTO_START

Write-Host "Authentication server has been installed as a Windows service."
Write-Host "You can start/stop the service from the Services management console."
Write-Host "Or use the following commands:"
Write-Host "  Start-Service AuthenticationServer"
Write-Host "  Stop-Service AuthenticationServer"
