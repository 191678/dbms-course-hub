# 数据库系统课程平台 - 前后端分离进程启动脚本
# 作用：以独立进程方式启动服务，不依附当前终端会话（终端关闭/回收不会杀掉服务）
# 日志：logs/ 目录下 backend/frontend 的 out/err 日志（每次启动自动归档旧日志）
# 适用场景：在用户自己的 PowerShell 窗口中手动执行（非沙箱环境）
# 用法：powershell -ExecutionPolicy Bypass -File scripts\start_services.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $root "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# 归档上一次运行的日志，保留排障历史
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
foreach ($name in @("backend", "frontend")) {
    foreach ($kind in @("out", "err")) {
        $log = Join-Path $logDir "$name.$kind.log"
        if (Test-Path $log) { Move-Item $log (Join-Path $logDir "$name.$kind.$stamp.log") -Force }
    }
}

function Test-PortListening {
    param([int]$Port)
    return [bool](netstat -ano | Select-String "[:.]$Port\s.*LISTENING")
}

function Start-Detached {
    param([string]$Name, [string]$FilePath, [string[]]$ArgumentList, [string]$WorkingDirectory, [int]$Port)
    if (Test-PortListening -Port $Port) {
        Write-Host "[$Name] 端口 $Port 已有服务监听，跳过启动"
        return
    }
    $proc = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList `
        -WorkingDirectory $WorkingDirectory -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logDir "$Name.out.log") `
        -RedirectStandardError  (Join-Path $logDir "$Name.err.log") -PassThru
    Write-Host "[$Name] 已启动 PID=$($proc.Id) 日志目录=$logDir"
}

# 后端 FastAPI（0.0.0.0:8000 兼容 IPv4/IPv6；不加 --reload，避免文件监控资源耗尽）
Start-Detached -Name "backend" -FilePath "python" `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000") `
    -WorkingDirectory (Join-Path $root "backend") -Port 8000

# 前端 Vite（host:true 同时绑定 IPv4/IPv6，避免 localhost 解析差异导致拒连）
Start-Detached -Name "frontend" -FilePath "npm.cmd" `
    -ArgumentList @("run", "dev") `
    -WorkingDirectory (Join-Path $root "frontend") -Port 5173

Write-Host "等待服务就绪..."
Start-Sleep -Seconds 8
foreach ($url in @("http://127.0.0.1:8000/api/realtime/version/", "http://127.0.0.1:5173/")) {
    try {
        $code = (Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 12).StatusCode
        Write-Host "$url -> $code"
    } catch {
        Write-Host "$url -> 未就绪或异常: $($_.Exception.Message)"
    }
}
Write-Host "完成。停止服务请运行 scripts\stop_services.ps1"
