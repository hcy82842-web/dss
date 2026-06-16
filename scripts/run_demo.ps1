$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Test-PortAvailable {
    param([int]$Port)

    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return $null -eq $connection
}

function Assert-PortAvailable {
    param(
        [int]$Port,
        [string]$ServiceName
    )

    if (-not (Test-PortAvailable -Port $Port)) {
        throw "$ServiceName 端口 $Port 已被占用。请关闭旧的演示命令行窗口后重新运行 run_demo.bat。"
    }
}

function Wait-HttpOk {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 20
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
                return $true
            }
        } catch {
            Start-Sleep -Seconds 1
        }
    }

    return $false
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

Write-Step "检查 Python 运行环境"
$Python = Resolve-Python
Write-Host "使用 Python $($Python.Version)"

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

if ((-not (Test-Path "artifacts\logistic_regression.joblib")) -or (-not (Test-Path "artifacts\model_metadata.json"))) {
    Write-Step "未发现模型产物，开始训练逻辑回归模型"
    & $VenvPython scripts\train_logistic_regression.py
}

Write-Step "检查演示端口"
Assert-PortAvailable -Port 8000 -ServiceName "FastAPI 后端"
Assert-PortAvailable -Port 8501 -ServiceName "Streamlit 前端"

Write-Step "启动 FastAPI 后端"
$BackendCommand = "cd /d `"$ProjectRoot`" && `"$VenvPython`" -m uvicorn src.dss_backend.main:create_default_app --factory --reload --host 127.0.0.1 --port 8000"
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $BackendCommand -WindowStyle Normal

Write-Step "等待后端健康检查"
if (-not (Wait-HttpOk -Url "http://127.0.0.1:8000/api/health" -TimeoutSeconds 20)) {
    throw "后端未能在 20 秒内通过健康检查。请查看 FastAPI 命令行窗口中的错误信息。"
}
Write-Host "后端已就绪：http://127.0.0.1:8000/api/health" -ForegroundColor Green

Write-Step "启动 Streamlit 前端"
$FrontendCommand = "cd /d `"$ProjectRoot`" && `"$VenvPython`" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501"
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $FrontendCommand -WindowStyle Normal

Write-Step "打开前端工作台"
Start-Sleep -Seconds 5
Start-Process "http://127.0.0.1:8501"

Write-Host ""
Write-Host "演示服务已启动：" -ForegroundColor Green
Write-Host "请使用前端工作台：http://127.0.0.1:8501"
Write-Host "后端 API 仅用于健康检查和接口调用：http://127.0.0.1:8000/api/health"
Write-Host "如果误打开 http://127.0.0.1:8000/，会看到后端提示信息，不是主页面。"
Write-Host ""
Write-Host "关闭演示时，直接关闭新打开的两个命令行窗口即可。"
