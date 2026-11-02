# 数据库系统课程平台 - 前后端服务停止脚本
# 按端口精确匹配进程后停止，不批量杀进程，避免误伤其他 node/python 进程
# 用法：powershell -ExecutionPolicy Bypass -File scripts\stop_services.ps1

foreach ($port in @(8000, 5173)) {
    $pids = netstat -ano | Select-String "[:.]$port\s.*LISTENING" | ForEach-Object {
        ($_ -split '\s+')[-1]
    } | Select-Object -Unique
    foreach ($p in $pids) {
        if ($p -match '^\d+$') {
            try {
                $procName = (Get-Process -Id $p -ErrorAction Stop).ProcessName
                Stop-Process -Id $p -Force -Confirm:$false
                Write-Host "端口 $port -> 已停止 $procName (PID=$p)"
            } catch {
                Write-Host "端口 $port -> PID=$p 停止失败: $($_.Exception.Message)"
            }
        }
    }
}
Write-Host "完成。"
