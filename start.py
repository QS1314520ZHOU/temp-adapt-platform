"""一键启动后端 + 前端"""
import subprocess
import sys
import os
import time

def main():
    base = os.path.dirname(os.path.abspath(__file__))

    # 启动后端
    backend_dir = os.path.join(base, "backend")
    print("[1/2] 启动后端 (http://localhost:8000) ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=backend_dir,
    )

    time.sleep(3)

    # 启动前端
    frontend_dir = os.path.join(base, "frontend")
    print("[2/2] 启动前端 (http://localhost:3000) ...")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=True,
    )

    print()
    print("=" * 50)
    print("  体温单回传适配平台 已启动")
    print("  后端: http://localhost:8000")
    print("  前端: http://localhost:3000")
    print("  文档: http://localhost:8000/docs")
    print("=" * 50)
    print("  按 Ctrl+C 停止所有服务")
    print("=" * 50)
    print()

    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("已停止。")

if __name__ == "__main__":
    main()
