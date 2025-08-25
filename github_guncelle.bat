@echo off
chcp 65001 >nul
echo.
echo 🔄 ReisBot Premium - GitHub'a Güncelleme
echo ======================================
echo.
if "%1"=="" (
    echo ❌ Kullanım: github_guncelle.bat <dosya_adi>
    echo Örnek: github_guncelle.bat main.py
    pause
    exit /b 1
)

python auto_updater.py güncelle %1
echo.
pause
