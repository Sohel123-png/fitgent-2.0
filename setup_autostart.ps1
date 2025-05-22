# PowerShell script to set up the authentication server to run on system startup

# Get the current directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$batchFilePath = Join-Path $scriptPath "start_auth_server.bat"

# Create a shortcut in the Windows Startup folder
$startupFolder = [System.Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupFolder "AuthServerAutostart.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $batchFilePath
$Shortcut.WorkingDirectory = $scriptPath
$Shortcut.Description = "Authentication Server Autostart"
$Shortcut.Save()

Write-Host "Authentication server has been set up to run automatically on system startup."
Write-Host "A shortcut has been created in: $shortcutPath"
Write-Host "You can also manually start the server by running start_auth_server.bat"
