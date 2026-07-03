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

REM 创建虚拟环境（优先使用 venv，降级到 virtualenv）
if not exist "backend\venv" (
    echo [1/6] 创建虚拟环境...
    cd backend
    python -m venv venv 2>nul
    if errorlevel 1 (
        echo [提示] venv 不可用，尝试 virtualenv...
        pip install virtualenv -q
        python -m virtualenv venv
    )
    cd ..
)

REM 激活虚拟环境
call "backend\venv\Scripts\activate.bat"

REM 安装依赖
echo [2/6] 检查依赖...
pip install -q -r backend\requirements.txt

REM 创建数据目录
if not exist "backend\data" mkdir backend\data
if not exist "backend\data\uploads" mkdir backend\data\uploads

REM 数据库初始化
echo [3/6] 初始化数据库...
cd backend
python init_data.py
cd ..

REM 检查前端
echo [4/6] 检查前端...
if not exist "backend\app\static" (
    echo [警告] 前端未构建，请在 frontend 目录运行:
    echo   npm install ^&^& npm run build
)

REM 复制 .env
if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env" >nul
    echo [提示] 已创建 .env 文件，请编辑配置后重新运行
)

REM 启动服务
echo [5/6] 启动服务...
echo [6/6] 访问 http://localhost:8000
echo.
timeout /t 2 /nobreak >nul
start http://localhost:8000
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
