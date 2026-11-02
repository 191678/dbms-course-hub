import subprocess
import time
import os

# 停止现有的Python进程
print("停止现有服务...")
subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
time.sleep(3)

# 启动新的后端服务
print("启动后端服务...")
os.chdir(r"e:\Program Files (x86)\Trae CN\trae_projects\shujukuxit\backend")

# 使用Python直接运行uvicorn
cmd = ['python', '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000']
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 等待服务器启动
time.sleep(5)

# 检查服务器是否启动
import requests
try:
    r = requests.get('http://localhost:8000/api/chapters/', timeout=5)
    if r.status_code == 200:
        print("✅ 后端服务已成功启动")
    else:
        print(f"后端服务返回异常状态: {r.status_code}")
except Exception as e:
    print(f"❌ 后端服务启动失败: {e}")
    # 读取错误日志
    stderr = process.stderr.read().decode('utf-8', errors='ignore')
    print(f"错误日志: {stderr[:500]}")

print("\n后端服务启动完成，请继续测试学习进度API。")