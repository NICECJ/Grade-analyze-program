@echo off
echo 启动成绩分析系统 (GradeInsights)
echo ================================

cd /d "%~dp0"

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 正在启动后端服务...
start "GradeInsights Backend" cmd /k "venv\Scripts\activate.bat && python start_backend.py"

echo 等待后端启动...
timeout /t 5 /nobreak >nul

echo 正在启动前端服务...
cd frontend
start "GradeInsights Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ================================
echo 系统启动完成！
echo.
echo 访问地址:
echo - 前端: http://localhost:3000
echo - 后端API: http://localhost:8000/docs
echo ================================

pause