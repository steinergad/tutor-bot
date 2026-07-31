#!/usr/bin/env powershell

Write-Host ""
Write-Host "====== OLLAMA + MISTRAL SETUP ======" -ForegroundColor Cyan
Write-Host ""

Write-Host "Your system: High-Performance (RTX 5070 + 31GB RAM)" -ForegroundColor Green
Write-Host "Model selected: Mistral 7B (4.1GB)" -ForegroundColor Green
Write-Host ""

# Check if Ollama is already installed
$ollama_path = "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama\ollama.exe"
if (Test-Path $ollama_path) {
    Write-Host "Ollama is already installed." -ForegroundColor Green
} else {
    Write-Host "Downloading and installing Ollama..." -ForegroundColor Yellow
    Write-Host "(This takes 2-5 minutes)"
    Write-Host ""
    
    # Download installer
    $installer = "$env:TEMP\OllamaSetup.exe"
    Write-Host "Downloading Ollama installer..."
    
    try {
        Invoke-WebRequest -Uri "https://ollama.ai/download/OllamaSetup.exe" -OutFile $installer -ErrorAction Stop
        Write-Host "Downloaded: $installer" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "Running installer (it will open a window)..." -ForegroundColor Yellow
        & $installer
        
        Write-Host "Waiting for installation to complete..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        
        # Wait for process to finish
        $count = 0
        while ((Get-Process OllamaSetup -ErrorAction SilentlyContinue) -and $count -lt 60) {
            Start-Sleep -Seconds 1
            $count++
        }
        
        Write-Host "Installation should be complete." -ForegroundColor Green
    } catch {
        Write-Host "Could not auto-download. Please download manually:" -ForegroundColor Yellow
        Write-Host "  1. Go to: https://ollama.ai/download" -ForegroundColor Cyan
        Write-Host "  2. Download 'Ollama for Windows'"
        Write-Host "  3. Run the installer"
        Write-Host "  4. Then run this script again"
        exit 1
    }
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Start Ollama service
Write-Host "Starting Ollama service..." -ForegroundColor Green

# Check if process is already running
if (Get-Process ollama -ErrorAction SilentlyContinue) {
    Write-Host "Ollama service already running." -ForegroundColor Green
} else {
    Write-Host "Starting Ollama..."
    Start-Process -FilePath $ollama_path -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "Ollama started." -ForegroundColor Green
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check if mistral is already installed
Write-Host "Checking for Mistral model..." -ForegroundColor Green

$ollama_exe = $ollama_path
if (-not (Test-Path $ollama_exe)) {
    # Fallback to PATH
    $ollama_exe = "ollama"
}

try {
    $models = & $ollama_exe list 2>&1 | Select-String "mistral"
    if ($models) {
        Write-Host "Mistral is already installed." -ForegroundColor Green
    } else {
        Write-Host "Mistral not found. Pulling model..." -ForegroundColor Yellow
        Write-Host "(This downloads 4.1GB - takes 5-15 minutes)" -ForegroundColor Yellow
        Write-Host ""
        
        & $ollama_exe pull mistral
        Write-Host ""
        Write-Host "Mistral downloaded successfully!" -ForegroundColor Green
    }
} catch {
    Write-Host "Could not check models. Proceeding anyway..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Configure .env
Write-Host "Configuring app.py to use Ollama..." -ForegroundColor Green

$env_file = ".env"
if (Test-Path $env_file) {
    $content = Get-Content $env_file -Raw
    # Remove other LLM configs
    $content = $content -replace "GITHUB_TOKEN=.*`n", ""
    $content = $content -replace "OPENAI_API_KEY=.*`n", ""
    # Add Ollama config
    if ($content -match "OLLAMA_BASE_URL=") {
        $content = $content -replace "OLLAMA_BASE_URL=.*", "OLLAMA_BASE_URL=http://localhost:11434"
    } else {
        if (-not $content.EndsWith("`n")) {
            $content += "`n"
        }
        $content += "OLLAMA_BASE_URL=http://localhost:11434`n"
    }
    if ($content -match "OLLAMA_LLM_MODEL=") {
        $content = $content -replace "OLLAMA_LLM_MODEL=.*", "OLLAMA_LLM_MODEL=mistral"
    } else {
        $content += "OLLAMA_LLM_MODEL=mistral`n"
    }
    if ($content -match "PROVIDER=") {
        $content = $content -replace "PROVIDER=.*", "PROVIDER=ollama"
    } else {
        $content += "PROVIDER=ollama`n"
    }
} else {
    $content = @"
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=mistral
PROVIDER=ollama
"@
}

Set-Content $env_file $content -Encoding UTF8
Write-Host "Saved to .env" -ForegroundColor Green

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:OLLAMA_LLM_MODEL = "mistral"
$env:PROVIDER = "ollama"

# Restart Streamlit
Write-Host "Restarting Streamlit app..." -ForegroundColor Green
taskkill /F /IM streamlit.exe 2>$null | Out-Null
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Starting app with Ollama + Mistral..." -ForegroundColor Cyan
Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

& streamlit run app.py
