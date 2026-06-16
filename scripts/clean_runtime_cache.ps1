$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

Write-Host "清理 Python 与 Streamlit 运行缓存..." -ForegroundColor Cyan

$cacheRoots = @("src", "tests", "scripts")

foreach ($root in $cacheRoots) {
    $fullPath = Join-Path $ProjectRoot $root
    if (Test-Path $fullPath) {
        Get-ChildItem -Path $fullPath -Directory -Recurse -Force -Filter "__pycache__" |
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    }
}

$pytestCache = Join-Path $ProjectRoot ".pytest_cache"
if (Test-Path $pytestCache) {
    Remove-Item -Path $pytestCache -Recurse -Force -ErrorAction SilentlyContinue
}

Get-ChildItem -Path $ProjectRoot -File -Force -Filter ".streamlit*.log" |
    Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "运行缓存清理完成。" -ForegroundColor Green
