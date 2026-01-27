@echo off
echo 成绩分析系统 (GradeInsights) 安装脚本
echo =====================================

echo.
echo 1. 安装Python依赖...
pip install -r requirements.txt

echo.
echo 2. 创建备份目录...
if not exist "backups" mkdir backups

echo.
echo 3. 初始化数据库...
python init_db.py

echo.
echo 4. 检查Excel文件...
python check_excel.py

echo.
echo 5. 安装前端依赖...
cd frontend
npm install
cd ..

echo.
echo =====================================
echo 安装完成！
echo.
echo 启动说明:
echo 1. 启动后端: python start_backend.py
echo 2. 启动前端: cd frontend && npm run dev
echo.
echo 访问地址:
echo - 前端: http://localhost:3000
echo - 后端API: http://localhost:8000/docs
echo =====================================

pause