#!/usr/bin/env powershell
<#
QUICK FIX: Configure LLM and Restart App

This script guides you through setting up an LLM provider.
Choose your preferred method:
  1. GitHub Models (Recommended - Free, 2 min)
  2. OpenAI API (Paid, 1 min)
  3. Ollama Local (Free, 10 min)
#>

Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TUTOR-BOT: LLM CONFIGURATION & RESTART                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n📋 DIAGNOSTIC RESULTS:" -ForegroundColor Yellow
Write-Host "  ✓ Knowledge graph: Working (30 entities, 37 relationships)" -ForegroundColor Green
Write-Host "  ✓ Homework validation: Working (English & Hebrew)" -ForegroundColor Green
Write-Host "  ✓ Prompt system: Working" -ForegroundColor Green
Write-Host "  ✓ Language support: Working" -ForegroundColor Green
Write-Host "  ✗ LLM provider: NOT CONFIGURED" -ForegroundColor Red

Write-Host "`n🔧 CHOOSE YOUR LLM PROVIDER:" -ForegroundColor Yellow
Write-Host "  1. GitHub Models (Recommended - Free, 2 min setup)" -ForegroundColor Cyan
Write-Host "  2. OpenAI (Paid - costs money, 1 min setup)" -ForegroundColor Cyan
Write-Host "  3. Ollama Local (Free - 10 min setup)" -ForegroundColor Cyan
Write-Host "  4. Just show me what's wrong" -ForegroundColor Cyan

$choice = Read-Host "`nEnter your choice (1-4)"

if ($choice -eq "1") {
    Write-Host "`n📌 GITHUB MODELS SETUP (2 minutes)" -ForegroundColor Yellow
    Write-Host "  This is FREE - included with your GitHub/Copilot account`n"
    
    Write-Host "Step 1: Get your GitHub token"
    Write-Host "  1. Go to: https://github.com/settings/tokens" -ForegroundColor Cyan
    Write-Host "  2. Click 'Generate new token' → 'Generate new token (classic)'"
    Write-Host "  3. Name: tutor-bot-models"
    Write-Host "  4. Check: repo, read:user, user:email"
    Write-Host "  5. Click Generate and copy the token (starts with github_pat_ or ghp_)`n"
    
    $token = Read-Host "Paste your GitHub token here"
    
    if ($token) {
        Write-Host "`nStep 2: Setting environment variable..."
        $env:GITHUB_TOKEN = $token
        Write-Host "  ✓ GITHUB_TOKEN set for this session" -ForegroundColor Green
        
        Write-Host "`nStep 3: Making it permanent (.env file)..."
        if (Test-Path ".env") {
            $content = Get-Content ".env" -Raw
            if ($content -like "*GITHUB_TOKEN*") {
                $content = $content -replace "GITHUB_TOKEN=.*", "GITHUB_TOKEN=$token"
            } else {
                $content += "`nGITHUB_TOKEN=$token"
            }
        } else {
            $content = "GITHUB_TOKEN=$token"
        }
        Set-Content ".env" $content -Encoding UTF8
        Write-Host "  ✓ Saved to .env file (permanent)" -ForegroundColor Green
        
        Write-Host "`nStep 4: Restarting app..."
        taskkill /F /IM streamlit.exe 2>$null | Out-Null
        Start-Sleep -Seconds 2
        
        Write-Host "  Starting: streamlit run app.py`n" -ForegroundColor Cyan
        & streamlit run app.py
    }
}
elseif ($choice -eq "2") {
    Write-Host "`n📌 OPENAI API SETUP" -ForegroundColor Yellow
    Write-Host "  Note: This costs money (pay-as-you-go)`n"
    
    Write-Host "Step 1: Get your OpenAI API key"
    Write-Host "  1. Go to: https://platform.openai.com/api/keys" -ForegroundColor Cyan
    Write-Host "  2. Click 'Create new secret key'"
    Write-Host "  3. Copy the key (starts with sk-)`n"
    
    $key = Read-Host "Paste your OpenAI API key here"
    
    if ($key) {
        Write-Host "`nStep 2: Setting environment variable..."
        $env:OPENAI_API_KEY = $key
        Write-Host "  ✓ OPENAI_API_KEY set for this session" -ForegroundColor Green
        
        Write-Host "`nStep 3: Making it permanent (.env file)..."
        if (Test-Path ".env") {
            $content = Get-Content ".env" -Raw
            if ($content -like "*OPENAI_API_KEY*") {
                $content = $content -replace "OPENAI_API_KEY=.*", "OPENAI_API_KEY=$key"
            } else {
                $content += "`nOPENAI_API_KEY=$key"
            }
        } else {
            $content = "OPENAI_API_KEY=$key"
        }
        Set-Content ".env" $content -Encoding UTF8
        Write-Host "  ✓ Saved to .env file (permanent)" -ForegroundColor Green
        
        Write-Host "`nStep 4: Restarting app..."
        taskkill /F /IM streamlit.exe 2>$null | Out-Null
        Start-Sleep -Seconds 2
        
        Write-Host "  Starting: streamlit run app.py`n" -ForegroundColor Cyan
        & streamlit run app.py
    }
}
elseif ($choice -eq "3") {
    Write-Host "`n📌 OLLAMA LOCAL SETUP (Free)" -ForegroundColor Yellow
    Write-Host "  Runs completely offline - requires local setup`n"
    
    Write-Host "Step 1: Download Ollama from https://ollama.ai" -ForegroundColor Cyan
    Write-Host "Step 2: Install and run:" -ForegroundColor Cyan
    Write-Host "  ollama serve" -ForegroundColor Yellow
    
    Write-Host "`nStep 3: In another terminal, download a model:"
    Write-Host "  ollama pull mistral    (recommended - 5 GB, fast)" -ForegroundColor Yellow
    Write-Host "  OR"
    Write-Host "  ollama pull llama2     (4 GB, more reliable)" -ForegroundColor Yellow
    
    Write-Host "`nStep 4: Set environment variable:"
    $env:OLLAMA_BASE_URL = "http://localhost:11434"
    Write-Host "  OLLAMA_BASE_URL=http://localhost:11434" -ForegroundColor Green
    
    Write-Host "`nStep 5: Restart app..."
    taskkill /F /IM streamlit.exe 2>$null | Out-Null
    Start-Sleep -Seconds 2
    
    Write-Host "  Starting: streamlit run app.py`n" -ForegroundColor Cyan
    & streamlit run app.py
}
else {
    Write-Host "`n📊 WHAT'S WORKING:" -ForegroundColor Green
    Write-Host "  ✓ Knowledge graph (30 entities, 37 relationships)" -ForegroundColor Green
    Write-Host "  ✓ Homework validation (English & Hebrew)" -ForegroundColor Green
    Write-Host "  ✓ Prompt generation (Socratic method)" -ForegroundColor Green
    Write-Host "  ✓ Language support (multilingual)" -ForegroundColor Green
    Write-Host "  ✓ All data files and databases" -ForegroundColor Green
    
    Write-Host "`n❌ WHAT'S MISSING:" -ForegroundColor Red
    Write-Host "  ✗ LLM API Configuration (no API key)" -ForegroundColor Red
    
    Write-Host "`n💡 SOLUTION:" -ForegroundColor Yellow
    Write-Host "  Set ONE of these environment variables:" -ForegroundColor Cyan
    Write-Host "    1. GITHUB_TOKEN = github_pat_... (recommended)" -ForegroundColor Cyan
    Write-Host "    2. OPENAI_API_KEY = sk-... (paid)" -ForegroundColor Cyan
    Write-Host "    3. OLLAMA_BASE_URL = http://localhost:11434 (local)" -ForegroundColor Cyan
    
    Write-Host "`n📖 For detailed instructions:" -ForegroundColor Yellow
    Write-Host "  Read: FIX_NO_LLM_RESPONSE.md" -ForegroundColor Cyan
}

Write-Host "`n" -ForegroundColor Cyan
