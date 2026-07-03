@echo off
chcp 65001 >nul
echo ========================================
echo   仓库人力数据分析系统 — 一键启动
echo ========================================

cd /d "%~dp0"

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请安装 Python 3.10+
    pause
    exit /b 1
)

REM 创建虚拟环境（使用 virtualenv，兼容无 venv 模块的 Python）
if not exist "backend\venv\Scripts\python.exe" (
    echo [1/5] 创建虚拟环境...
    pip install virtualenv -q 2>nul
    cd backend
    python -m virtualenv venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    cd ..
)

REM 激活虚拟环境
call "backend\venv\Scripts\activate.bat"

REM 安装依赖
echo [2/5] 安装依赖...
pip install -q -r backend\requirements.txt

REM 创建数据目录
if not exist "backend\data" mkdir backend\data
if not exist "backend\data\uploads" mkdir backend\data\uploads

REM 数据库初始化
echo [3/5] 初始化数据库...
cd backend
python init_data.py
cd ..

REM 检查前端
echo [4/5] 检查前端...
if not exist "backend\app\static\index.html" (
    echo [警告] 前端未构建，图表页面将无法访问
    echo        请在 frontend 目录运行: npm install ^&^& npm run build
)

REM 复制 .env
if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env" >nul
    echo [提示] 已创建 .env 文件
)

REM 启动服务
echo [5/5] 启动服务...
echo.
echo ========================================
echo   访问地址: http://localhost:8000
echo   默认账号: admin / admin123
echo   按 Ctrl+C 停止服务
echo ========================================
echo.
timeout /t 2 /nobreak >nul
start http://localhost:8000
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
pause