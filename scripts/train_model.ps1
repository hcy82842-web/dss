$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Resolve-Python {
    $candidates = @(
        @("py", "-3.11"),
        @("py", "-3.12"),
        @("py", "-3.10"),
        @("python", "")
    )

    foreach ($candidate in $candidates) {
        $exe = $candidate[0]
        $arg = $candidate[1]
        try {
            if ($arg) {
                $version = & $exe $arg -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
            } else {
                $version = & $exe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
            }
            if ($LASTEXITCODE -eq 0) {
                $parts = $version.Trim().Split(".")
                if ([int]$parts[0] -eq 3 -and [int]$parts[1] -ge 10) {
                    return @{ Exe = $exe; Arg = $arg; Version = $version.Trim() }
                }
            }
        } catch {
            continue
        }
    }

    throw "未找到 Python 3.10+。请先安装 Python 3.10 或更高版本。"
}

function Invoke-ProjectPython {
    param(
        [hashtable]$Python,
        [string[]]$Args
    )

    if ($Python.Arg) {
        & $Python.Exe $Python.Arg @Args
    } else {
        & $Python.Exe @Args
    }
}

function Assert-RequiredFile {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        throw "训练后仍缺少必要文件：$Path"
    }
}

Write-Step "检查 Python 运行环境"
$Python = Resolve-Python
Write-Host "使用 Python $($Python.Version)"

Write-Step "清理旧运行缓存"
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "clean_runtime_cache.ps1")

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Step "创建虚拟环境 .venv"
    Invoke-ProjectPython -Python $Python -Args @("-m", "venv", ".venv")
}

Write-Step "安装或更新依赖"
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r requirements.txt

if (-not (Test-Path "data\bank-additional-full.csv")) {
    throw "缺少 data\bank-additional-full.csv。请先将 UCI Bank Marketing 数据文件放入 data 目录。"
}

Write-Step "训练逻辑回归模型并生成验证集结果"
& $VenvPython scripts\train_logistic_regression.py
if ($LASTEXITCODE -ne 0) {
    throw "模型训练失败。请查看上方 Python 错误信息。"
}

Write-Step "校验训练产物"
Assert-RequiredFile "artifacts\logistic_regression.joblib"
Assert-RequiredFile "artifacts\model_metadata.json"
Assert-RequiredFile "artifacts\validation_predictions.csv"
Assert-RequiredFile "artifacts\evaluation_summary.json"

& $VenvPython -c "import pandas as pd; from src.dss_backend.ml.inference import load_model_bundle, predict_probability_for_customer; bundle = load_model_bundle('artifacts/logistic_regression.joblib', 'artifacts/model_metadata.json'); row = pd.read_csv('artifacts/validation_predictions.csv').iloc[0].to_dict(); probability = predict_probability_for_customer(bundle, row); assert 0 <= probability <= 1; print('model artifact self-check ok')"
if ($LASTEXITCODE -ne 0) {
    throw "模型产物自检失败。请重新运行 train_model.bat。"
}

Write-Host ""
Write-Host "训练完成，已生成以下文件：" -ForegroundColor Green
Write-Host "- artifacts\logistic_regression.joblib"
Write-Host "- artifacts\model_metadata.json"
Write-Host "- artifacts\validation_predictions.csv"
Write-Host "- artifacts\evaluation_summary.json"
Write-Host ""
Write-Host "下一步可以运行 run_demo.bat 启动前端和后端。"
