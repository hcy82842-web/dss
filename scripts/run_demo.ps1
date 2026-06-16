$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot
$LogPath = Join-Path $ProjectRoot "artifacts\run_demo.log"

function Initialize-Log {
    $logDir = Split-Path $LogPath -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir | Out-Null
    }
    "==== run_demo started $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====" | Set-Content -Path $LogPath -Encoding UTF8
}

function Write-Log {
    param([string]$Message)
    Add-Content -Path $LogPath -Value "[$(Get-Date -Format 'HH:mm:ss')] $Message" -Encoding UTF8
}

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
    Write-Log $Message
}

function Fail-Friendly {
    param([string]$Message)
    throw [System.Exception]::new($Message)
}

function Get-PortListeners {
    param([int]$Port)
    return @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

function Test-PortAvailable {
    param([int]$Port)
    return (Get-PortListeners -Port $Port).Count -eq 0
}

function Format-PortOwner {
    param($Connection)

    $process = Get-Process -Id $Connection.OwningProcess -ErrorAction SilentlyContinue
    $name = if ($process) { $process.ProcessName } else { "未知进程" }
    $path = ""
    try {
        $path = (Get-CimInstance Win32_Process -Filter "ProcessId=$($Connection.OwningProcess)" -ErrorAction Stop).ExecutablePath
    } catch {
        $path = ""
    }

    $text = "- PID: $($Connection.OwningProcess)`n  进程名: $name"
    if ($path) {
        $text += "`n  路径: $path"
    }
    return $text
}

function Assert-PortAvailable {
    param(
        [int]$Port,
        [string]$ServiceName
    )

    $listeners = Get-PortListeners -Port $Port
    if ($listeners.Count -eq 0) {
        Write-Log "$ServiceName port $Port is available"
        return
    }

    $owners = ($listeners | ForEach-Object { Format-PortOwner -Connection $_ }) -join "`n"
    Fail-Friendly @"
$ServiceName 端口 $Port 已被占用

占用进程：
$owners

处理方法：
1. 关闭旧的 FastAPI / Streamlit 命令行窗口
2. 重新运行 run_demo.bat
"@
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

function Assert-RequiredFile {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        Fail-Friendly "缺少必要文件：$Path。请先运行 .\.venv\Scripts\python.exe scripts\train_logistic_regression.py"
    }
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

    Fail-Friendly "未找到 Python 3.10+。请先安装 Python 3.10 或更高版本。"
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

function Invoke-Main {
    Initialize-Log

    Write-Step "检查 Python 运行环境"
    $Python = Resolve-Python
    Write-Host "使用 Python $($Python.Version)"
    Write-Log "Using Python $($Python.Version)"

    Write-Step "清理旧运行缓存"
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "clean_runtime_cache.ps1")
    if ($LASTEXITCODE -ne 0) {
        Fail-Friendly "缓存清理失败。详细日志：artifacts\run_demo.log"
    }

    $VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $VenvPython)) {
        Write-Step "创建虚拟环境 .venv"
        Invoke-ProjectPython -Python $Python -Args @("-m", "venv", ".venv")
        if ($LASTEXITCODE -ne 0) {
            Fail-Friendly "虚拟环境创建失败。请检查 Python 安装。"
        }
    }

    Write-Step "安装或更新依赖"
    & $VenvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        Fail-Friendly "pip 升级失败。详细日志：artifacts\run_demo.log"
    }
    & $VenvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Fail-Friendly "依赖安装失败。详细日志：artifacts\run_demo.log"
    }

    if (-not (Test-Path "data\bank-additional-full.csv")) {
        Fail-Friendly "缺少 data\bank-additional-full.csv。请先将 UCI Bank Marketing 数据文件放入 data 目录。"
    }

    if ((-not (Test-Path "artifacts\logistic_regression.joblib")) -or (-not (Test-Path "artifacts\model_metadata.json"))) {
        Write-Step "未发现模型产物，开始训练逻辑回归模型"
        & $VenvPython scripts\train_logistic_regression.py
        if ($LASTEXITCODE -ne 0) {
            Fail-Friendly "模型训练失败。请查看上方 Python 输出。"
        }
    }

    Write-Step "执行启动前自检"
    Assert-RequiredFile "artifacts\logistic_regression.joblib"
    Assert-RequiredFile "artifacts\model_metadata.json"
    Assert-RequiredFile "artifacts\validation_predictions.csv"
    Assert-RequiredFile "artifacts\evaluation_summary.json"
    & $VenvPython -c "from src.dss_frontend.llm_cards import build_structured_llm_sections; import app; print('startup import self-check ok')"
    if ($LASTEXITCODE -ne 0) {
        Fail-Friendly "启动前 import 自检失败。请确认已拉取最新代码，并关闭旧 Streamlit/FastAPI 窗口后重试。"
    }

    Write-Step "检查演示端口"
    Assert-PortAvailable -Port 8000 -ServiceName "FastAPI 后端"
    Assert-PortAvailable -Port 8501 -ServiceName "Streamlit 前端"

    Write-Step "启动 FastAPI 后端"
    $BackendCommand = "cd /d `"$ProjectRoot`" && `"$VenvPython`" -m uvicorn src.dss_backend.main:create_default_app --factory --reload --host 127.0.0.1 --port 8000"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $BackendCommand -WindowStyle Normal

    Write-Step "等待后端健康检查"
    if (-not (Wait-HttpOk -Url "http://127.0.0.1:8000/api/health" -TimeoutSeconds 20)) {
        Fail-Friendly "后端未能在 20 秒内通过健康检查。请查看 FastAPI 命令行窗口中的错误信息。"
    }
    Write-Host "后端已就绪：http://127.0.0.1:8000/api/health" -ForegroundColor Green

    Write-Step "启动 Streamlit 前端"
    $FrontendCommand = "cd /d `"$ProjectRoot`" && `"$VenvPython`" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $FrontendCommand -WindowStyle Normal

    Write-Step "等待前端工作台就绪"
    if (-not (Wait-HttpOk -Url "http://127.0.0.1:8501" -TimeoutSeconds 40)) {
        Fail-Friendly "前端未能在 40 秒内启动。请查看 Streamlit 命令行窗口中的错误信息。"
    }
    Write-Host "前端已就绪：http://127.0.0.1:8501" -ForegroundColor Green

    Write-Step "打开前端工作台"
    Start-Process "http://127.0.0.1:8501"

    Write-Host ""
    Write-Host "演示服务已启动：" -ForegroundColor Green
    Write-Host "请使用前端工作台：http://127.0.0.1:8501"
    Write-Host "后端 API 仅用于健康检查和接口调用：http://127.0.0.1:8000/api/health"
    Write-Host "如果误打开 http://127.0.0.1:8000/，会看到后端提示信息，不是主页面。"
    Write-Host ""
    Write-Host "关闭演示时，直接关闭新打开的两个命令行窗口即可。"
    Write-Log "Demo started successfully"
}

try {
    Invoke-Main
    exit 0
} catch {
    $message = $_.Exception.Message
    Write-Host ""
    Write-Host "启动失败：" -ForegroundColor Red
    Write-Host $message -ForegroundColor Yellow
    Write-Host ""
    Write-Host "详细日志：artifacts\run_demo.log" -ForegroundColor Cyan
    try {
        Write-Log "ERROR: $message"
    } catch {
        # Ignore logging errors during failure reporting.
    }
    exit 1
}
