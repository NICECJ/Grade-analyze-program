# 数据库配置脚本
Write-Host "=== 数据库配置 ===" -ForegroundColor Green

Write-Host "请输入 MariaDB root 用户的密码:" -ForegroundColor Yellow
$rootPassword = Read-Host -AsSecureString
$rootPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($rootPassword))

# 测试连接并创建数据库
Write-Host "正在创建数据库..." -ForegroundColor Yellow
$createDbCommand = "CREATE DATABASE IF NOT EXISTS grade_insights CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

try {
    # 使用 mysql 命令创建数据库
    $env:MYSQL_PWD = $rootPasswordPlain
    mysql -u root -e $createDbCommand
    Write-Host "✅ 数据库创建成功" -ForegroundColor Green
    
    # 更新 .env 文件
    $envPath = "code\.env"
    $envContent = Get-Content $envPath -Raw
    $newDbUrl = "DATABASE_URL=mysql+aiomysql://root:${rootPasswordPlain}@localhost:3306/grade_insights"
    $envContent = $envContent -replace "DATABASE_URL=.*", $newDbUrl
    Set-Content $envPath $envContent -Encoding UTF8
    Write-Host "✅ 环境配置已更新" -ForegroundColor Green
    
} catch {
    Write-Host "❌ 数据库配置失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "请检查密码是否正确" -ForegroundColor Yellow
    exit 1
} finally {
    # 清除环境变量中的密码
    Remove-Item Env:MYSQL_PWD -ErrorAction SilentlyContinue
}

Write-Host "✅ 数据库配置完成！" -ForegroundColor Green