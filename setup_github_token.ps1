#!/usr/bin/env powershell

Write-Host ""
Write-Host "====== GITHUB MODELS SETUP (FREE - 2 MINUTES) ======" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Opening GitHub token page in browser..." -ForegroundColor Green
Start-Process "https://github.com/settings/tokens"
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "INSTRUCTIONS IN YOUR BROWSER:" -ForegroundColor Yellow
Write-Host "1. Click 'Generate new token' > 'Generate new token (classic)'"
Write-Host "2. Name: tutor-bot-models"
Write-Host "3. Check permissions:"
Write-Host "   - repo"
Write-Host "   - read:user"
Write-Host "   - user:email"
Write-Host "4. Click 'Generate token' at the bottom"
Write-Host "5. Copy the token (starts with github_pat_ or ghp_)"
Write-Host ""

$token = Read-Host "Paste your GitHub token here"

if (-not $token) {
    Write-Host "No token provided. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Token received! Setting up..." -ForegroundColor Green

# Save to .env
$env_file = ".env"
if (Test-Path $env_file) {
    $content = Get-Content $env_file -Raw
    if ($content -match "GITHUB_TOKEN=") {
        $content = $content -replace "GITHUB_TOKEN=.*", "GITHUB_TOKEN=$token"
    } else {
        if (-not $content.EndsWith("`n")) {
            $content += "`n"
        }
        $content += "GITHUB_TOKEN=$token`n"
    }
} else {
    $content = "GITHUB_TOKEN=$token`n"
}

Set-Content $env_file $content -Encoding UTF8
Write-Host "Saved to .env file" -ForegroundColor Green

# Set for this session
$env:GITHUB_TOKEN = $token

# Stop old instance
Write-Host ""
Write-Host "Stopping old Streamlit instance..." -ForegroundColor Green
taskkill /F /IM streamlit.exe 2>$null | Out-Null
Start-Sleep -Seconds 1

# Start new instance
Write-Host "Starting Streamlit app..." -ForegroundColor Green
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

& streamlit run app.py
