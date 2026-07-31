#!/usr/bin/env powershell

Write-Host ""
Write-Host "====== SWITCHING TO OPENAI (WORKS RELIABLY) ======" -ForegroundColor Cyan
Write-Host ""

Write-Host "GitHub Models didn't work (401 error), but OpenAI will work immediately." -ForegroundColor Yellow
Write-Host "Cost: ~$0.15-0.50 per conversation (you control)" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Get your OpenAI API key" -ForegroundColor Green
Write-Host "  1. Go to: https://platform.openai.com/api/keys" -ForegroundColor Cyan
Write-Host "  2. Click 'Create new secret key'"
Write-Host "  3. Copy it (starts with sk-)"
Write-Host ""

$key = Read-Host "Paste your OpenAI API key"

if (-not $key) {
    Write-Host "No key provided. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setting up OpenAI..." -ForegroundColor Green

# Update .env
$env_file = ".env"
if (Test-Path $env_file) {
    $content = Get-Content $env_file -Raw
    # Remove GITHUB_TOKEN if exists
    $content = $content -replace "GITHUB_TOKEN=.*`n", ""
    # Add OPENAI_API_KEY
    if ($content -match "OPENAI_API_KEY=") {
        $content = $content -replace "OPENAI_API_KEY=.*", "OPENAI_API_KEY=$key"
    } else {
        if (-not $content.EndsWith("`n")) {
            $content += "`n"
        }
        $content += "OPENAI_API_KEY=$key`n"
    }
} else {
    $content = "OPENAI_API_KEY=$key`n"
}

Set-Content $env_file $content -Encoding UTF8
Write-Host "Saved to .env" -ForegroundColor Green

# Set for this session
$env:OPENAI_API_KEY = $key

# Restart
Write-Host ""
Write-Host "Restarting Streamlit with OpenAI..." -ForegroundColor Green
taskkill /F /IM streamlit.exe 2>$null | Out-Null
Start-Sleep -Seconds 1

Write-Host ""
Write-Host "Starting app..." -ForegroundColor Cyan
Write-Host ""

& streamlit run app.py
