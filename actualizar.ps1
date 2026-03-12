$PROJECT_DIR = "D:\DemocracIA"
Set-Location $PROJECT_DIR
Write-Host "📥 Bajando cambios de GitHub..." -ForegroundColor Yellow
git pull origin main
Write-Host "✅ Proyecto actualizado." -ForegroundColor Green
