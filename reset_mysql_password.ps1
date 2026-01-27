# MariaDB 密码重置脚本
Write-Host "=== MariaDB 密码重置 ===" -ForegroundColor Green

Write-Host "正在停止 MariaDB 服务..." -ForegroundColor Yellow
try {
    Stop-Service -Name "MariaDB" -Force
    Write-Host "✅ MariaDB 服务已停止" -ForegroundColor Green
} catch {
    Write-Host "⚠️  停止服务失败，可能需要管理员权限" -ForegroundColor Yellow
}

Write-Host "`n请按照以下步骤重置密码:" -ForegroundColor Yellow
Write-Host "1. 以管理员身份打开命令提示符" -ForegroundColor Cyan
Write-Host "2. 运行以下命令:" -ForegroundColor Cyan
Write-Host "   net stop MariaDB" -ForegroundColor White
Write-Host "   mysqld --skip-grant-tables --skip-networking" -ForegroundColor White
Write-Host "3. 打开新的命令提示符窗口，运行:" -ForegroundColor Cyan
Write-Host "   mysql -u root" -ForegroundColor White
Write-Host "   USE mysql;" -ForegroundColor White
Write-Host "   UPDATE user SET password=PASSWORD('123456') WHERE User='root';" -ForegroundColor White
Write-Host "   FLUSH PRIVILEGES;" -ForegroundColor White
Write-Host "   EXIT;" -ForegroundColor White
Write-Host "4. 关闭 mysqld 进程，重启 MariaDB 服务" -ForegroundColor Cyan
Write-Host "   net start MariaDB" -ForegroundColor White

Write-Host "`n或者使用更简单的方法:" -ForegroundColor Yellow
Write-Host "重新安装 MariaDB 并设置新密码" -ForegroundColor Cyan