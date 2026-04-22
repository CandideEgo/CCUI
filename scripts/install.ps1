# Claude Status Bar Installer (Windows PowerShell)
# Installs the Claude Code status bar script and configures settings.json

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$ClaudaDir = "$env:USERPROFILE\.claude"
$StatuslineDir = "$ClaudaDir\statusline"
$SettingsFile = "$ClaudaDir\settings.json"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

Write-Host "Installing Claude Status Bar..." -ForegroundColor Cyan

# Create directories
New-Item -ItemType Directory -Force -Path $StatuslineDir | Out-Null

# Copy scripts
Copy-Item "$ProjectDir\status.py" "$StatuslineDir\" -Force
Copy-Item "$ProjectDir\debug.py" "$StatuslineDir\" -Force
Copy-Item "$ProjectDir\scripts\init_baseline.py" "$StatuslineDir\" -Force

# Detect Python command
$PythonCmd = "python"
try {
    $null = Get-Command python -ErrorAction Stop
} catch {
    $PythonCmd = "py"
    try {
        $null = Get-Command $PythonCmd -ErrorAction Stop
    } catch {
        Write-Host "Error: Python not found. Please install Python 3." -ForegroundColor Red
        exit 1
    }
}

# Get absolute path to status.py
$StatusPyPath = "$StatuslineDir\status.py"

# Configure settings.json
function Configure-Settings {
    if (Test-Path $SettingsFile) {
        $content = Get-Content $SettingsFile -Raw -Encoding UTF8
        $settings = $null

        try {
            $settings = $content | ConvertFrom-Json
        } catch {
            Write-Host "Warning: settings.json is not valid JSON. Creating new one." -ForegroundColor Yellow
            $settings = @{}
        }

        if ($settings.PSObject.Properties.Name -contains "statusLine" -and -not $Force) {
            Write-Host "statusLine already configured in $SettingsFile" -ForegroundColor Yellow
            Write-Host "Use -Force to overwrite."
        } else {
            $settings | Add-Member -NotePropertyName "statusLine" -NotePropertyValue @{
                type = "command"
                command = "$PythonCmd `"$StatusPyPath`""
            } -Force

            $settings | ConvertTo-Json -Depth 10 | Set-Content $SettingsFile -Encoding UTF8
            Write-Host "Updated $SettingsFile" -ForegroundColor Green
        }
    } else {
        # Create new settings.json
        New-Item -ItemType Directory -Force -Path $ClaudaDir | Out-Null
        $newSettings = @{
            statusLine = @{
                type = "command"
                command = "$PythonCmd `"$StatusPyPath`""
            }
        }
        $newSettings | ConvertTo-Json -Depth 10 | Set-Content $SettingsFile -Encoding UTF8
        Write-Host "Created $SettingsFile" -ForegroundColor Green
    }
}

Configure-Settings

# Auto-run baseline initialization
Write-Host ""
Write-Host "Running baseline initialization..." -ForegroundColor Cyan
& $PythonCmd "$StatuslineDir\init_baseline.py"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Baseline captured successfully!" -ForegroundColor Green
} else {
    Write-Host "Baseline initialization failed (Claude Code may not be configured yet)." -ForegroundColor Yellow
    Write-Host "You can run: python `"$StatuslineDir\init_baseline.py`"" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "Restart Claude Code to see the status bar."
Write-Host ""
Write-Host "Debug: Logs are written to $StatuslineDir\debug.log"
