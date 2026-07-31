#!/usr/bin/env powershell

Write-Host ""
Write-Host "================== SYSTEM STATS ==================" -ForegroundColor Cyan
Write-Host ""

# RAM
$ram = Get-CimInstance Win32_ComputerSystem | Select-Object -ExpandProperty TotalPhysicalMemory
$ram_gb = [math]::Round($ram / 1GB, 1)
Write-Host "[RAM] $ram_gb GB"

# CPU
$cpu = Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name
$cores = (Get-CimInstance Win32_Processor | Select-Object -ExpandProperty NumberOfCores)[0]
$logical = (Get-CimInstance Win32_Processor | Select-Object -ExpandProperty NumberOfLogicalProcessors)[0]
Write-Host "[CPU] $cpu"
Write-Host "      Cores: $cores | Logical: $logical"

# GPU
Write-Host ""
Write-Host "[GPU] Checking..."
$gpu = Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name
if ($gpu) {
    foreach ($g in $gpu) {
        Write-Host "      - $g"
    }
    if ($gpu -match "NVIDIA|GeForce|RTX|GTX|Tesla") {
        Write-Host "      NVIDIA GPU detected (CUDA available)"
    }
} else {
    Write-Host "      No dedicated GPU (CPU only)"
}

# Disk
$disk = Get-Volume | Where-Object { $_.DriveLetter -eq 'C' } | Select-Object -ExpandProperty SizeRemaining
$disk_gb = [math]::Round($disk / 1GB, 1)
Write-Host ""
Write-Host "[DISK] C: drive has $disk_gb GB free"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "RECOMMENDATIONS:" -ForegroundColor Yellow
Write-Host ""

if ($ram_gb -ge 16 -and $cores -ge 8) {
    Write-Host "[HIGH-PERFORMANCE] Excellent system!" -ForegroundColor Green
    Write-Host "  Best models:"
    Write-Host "  - mistral (7B, 4.1GB) - RECOMMENDED"
    Write-Host "  - llama2 (7B, 3.8GB) - Great alternative"
    Write-Host "  - neural-chat (7B, 4.7GB) - Fastest"
    $recommended = "mistral"
} elseif ($ram_gb -ge 12 -and $cores -ge 6) {
    Write-Host "[MID-RANGE] Good machine" -ForegroundColor Green
    Write-Host "  Best models:"
    Write-Host "  - mistral (7B, 4.1GB) - RECOMMENDED"
    Write-Host "  - phi (3.8B, 2.4GB) - Lightweight"
    $recommended = "mistral"
} elseif ($ram_gb -ge 8 -and $cores -ge 4) {
    Write-Host "[ENTRY-LEVEL] Limited but workable" -ForegroundColor Yellow
    Write-Host "  Best models:"
    Write-Host "  - phi (3.8B, 2.4GB) - RECOMMENDED"
    Write-Host "  - orca-mini (3B, 1.7GB) - Very lightweight"
    $recommended = "phi"
} else {
    Write-Host "[MINIMAL] Limited resources" -ForegroundColor Yellow
    Write-Host "  Best models:"
    Write-Host "  - orca-mini (3B, 1.7GB) - RECOMMENDED"
    Write-Host "  Warning: Slower responses but should work"
    $recommended = "orca-mini"
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "SELECTED: $recommended" -ForegroundColor Green
Write-Host ""
