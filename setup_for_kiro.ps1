# 针对当前 Kiro 环境的配置脚本
Write-Host "=== 成绩分析系统 Kiro 环境配置 ===" -ForegroundColor Green

# 设置 Python 路径
$pythonPath = "E:\Codeapp\Python\Python3.13\python.exe"
$pipPath = "E:\Codeapp\Python\Python3.13\Scripts\pip.exe"

Write-Host "✅ 检测到 Python 3.13.3" -ForegroundColor Green
Write-Host "Python 路径: $pythonPath" -ForegroundColor Cyan

# 1. 配置项目环境
Write-Host "`n🔧 步骤 1: 配置项目环境" -ForegroundColor Cyan

# 创建 .env 文件
if (-not (Test-Path "code\.env")) {
    if (Test-Path "code\.env.example") {
        Copy-Item "code\.env.example" "code\.env"
        Write-Host "✅ 创建 .env 配置文件" -ForegroundColor Green
    }
}

# 进入项目目录
Set-Location "code"

# 创建虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "创建 Python 虚拟环境..." -ForegroundColor Yellow
    & $pythonPath -m venv venv
    Write-Host "✅ 虚拟环境创建完成" -ForegroundColor Green
}

# 安装 Python 依赖
Write-Host "安装 Python 依赖..." -ForegroundColor Yellow
& "venv\Scripts\python.exe" -m pip install --upgrade pip
& "venv\Scripts\pip.exe" install -r requirements.txt
Write-Host "✅ Python 依赖安装完成" -ForegroundColor Green

# 2. 安装前端依赖
Write-Host "`n📦 步骤 2: 安装前端依赖" -ForegroundColor Cyan
Set-Location "frontend"
if (-not (Test-Path "node_modules")) {
    Write-Host "安装前端依赖..." -ForegroundColor Yellow
    npm install
    Write-Host "✅ 前端依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "✅ 前端依赖已存在" -ForegroundColor Green
}
Set-Location ".."

# 3. 配置数据库
Write-Host "`n🗄️  步骤 3: 配置数据库" -ForegroundColor Cyan

# 检查 MariaDB 服务
try {
    $service = Get-Service -Name "MariaDB" -ErrorAction SilentlyContinue
    if ($service) {
        if ($service.Status -ne "Running") {
            Write-Host "启动 MariaDB 服务..." -ForegroundColor Yellow
            Start-Service -Name "MariaDB"
        }
        Write-Host "✅ MariaDB 服务正在运行" -ForegroundColor Green
    } else {
        Write-Host "⚠️  MariaDB 服务未找到，请检查服务名称" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  无法检查 MariaDB 服务状态" -ForegroundColor Yellow
}

# 提示配置数据库连接
Write-Host "`n数据库配置说明:" -ForegroundColor Yellow
Write-Host "1. 确保 MariaDB/MySQL 服务正在运行" -ForegroundColor Cyan
Write-Host "2. 创建数据库: CREATE DATABASE grade_insights;" -ForegroundColor Cyan
Write-Host "3. 检查 .env 文件中的数据库连接配置" -ForegroundColor Cyan

$configDb = Read-Host "`n是否现在配置数据库连接信息? (y/n)"
if ($configDb -eq "y" -or $configDb -eq "Y") {
    Write-Host "`n请输入数据库连接信息:" -ForegroundColor Yellow
    
    $dbHost = Read-Host "数据库主机 (默认: localhost)"
    if ([string]::IsNullOrEmpty($dbHost)) { $dbHost = "localhost" }
    
    $dbPort = Read-Host "数据库端口 (默认: 3306)"
    if ([string]::IsNullOrEmpty($dbPort)) { $dbPort = "3306" }
    
    $dbUser = Read-Host "数据库用户名 (默认: root)"
    if ([string]::IsNullOrEmpty($dbUser)) { $dbUser = "root" }
    
    $dbPassword = Read-Host "数据库密码"
    
    $dbName = Read-Host "数据库名称 (默认: grade_insights)"
    if ([string]::IsNullOrEmpty($dbName)) { $dbName = "grade_insights" }
    
    # 更新 .env 文件
    $envContent = Get-Content ".env" -Raw
    $newDbUrl = "DATABASE_URL=mysql+aiomysql://${dbUser}:${dbPassword}@${dbHost}:${dbPort}/${dbName}"
    $envContent = $envContent -replace "DATABASE_URL=.*", $newDbUrl
    Set-Content ".env" $envContent -Encoding UTF8
    
    Write-Host "✅ 数据库配置已更新" -ForegroundColor Green
}

# 4. 初始化数据库
Write-Host "`n🔄 步骤 4: 初始化数据库" -ForegroundColor Cyan
$initDb = Read-Host "是否现在初始化数据库表? (y/n)"
if ($initDb -eq "y" -or $initDb -eq "Y") {
    Write-Host "初始化数据库表..." -ForegroundColor Yellow
    try {
        & "venv\Scripts\python.exe" init_db.py
        Write-Host "✅ 数据库初始化完成" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  数据库初始化失败，请检查连接配置" -ForegroundColor Yellow
        Write-Host "错误信息: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Set-Location ".."

# 5. 创建启动脚本
Write-Host "`n📝 步骤 5: 创建启动脚本" -ForegroundColor Cyan

# 创建适合当前环境的启动脚本
$startScript = @'
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
'@

Set-Content "code\start_system.bat" $startScript -Encoding ASCII
Write-Host "✅ 创建启动脚本: code\start_system.bat" -ForegroundColor Green

# 6. 完成配置
Write-Host "`n🎉 配置完成!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "Kiro 环境配置已完成！" -ForegroundColor Yellow
Write-Host "" -ForegroundColor Yellow
Write-Host "启动方式:" -ForegroundColor Yellow
Write-Host "1. 双击运行: code\start_system.bat" -ForegroundColor Cyan
Write-Host "2. 或者手动启动后端和前端" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Yellow
Write-Host "访问地址:" -ForegroundColor Yellow
Write-Host "- 前端界面: http://localhost:3000" -ForegroundColor Cyan
Write-Host "- 后端API文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Green

$startNow = Read-Host "`n是否现在启动系统? (y/n)"
if ($startNow -eq "y" -or $startNow -eq "Y") {
    Write-Host "正在启动系统..." -ForegroundColor Yellow
    Start-Process -FilePath "code\start_system.bat"
    Write-Host "✅ 系统启动中，请查看新打开的窗口" -ForegroundColor Green
}