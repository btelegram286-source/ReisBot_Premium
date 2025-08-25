@echo off
chcp 65001 >nul
echo.
echo 🗑️ ReisBot Premium - GitHub'dan Dosya Silme
echo ==========================================
echo.
if "%1"=="" (
    echo ❌ Kullanım: github_sil.bat <dosya_adi>
    echo Örnek: github_sil.bat main.py
    pause
    exit /b 1
)

python auto_updater.py sil %1
echo.
pause
