@echo off
chcp 65001 >nul
echo.
echo 🔧 Bot İsmi Değiştirme Aracı
echo ============================
echo.

if "%1"=="" (
    echo ❌ Kullanım: isim_degistir.bat <yeni_isim>
    echo Örnek: isim_degistir.bat SuperBot
    pause
    exit /b 1
)

set NEW_NAME=%1

echo Eski isim: ReisBot
echo Yeni isim: %NEW_NAME%
echo.
echo ⚠️  Bu işlem geri alınamaz! Devam etmek istiyor musunuz?
echo.
choice /c EN /n /m "Evet için E, Hayır için N: "

if errorlevel 2 (
    echo.
    echo ❌ İşlem iptal edildi.
    pause
    exit /b 0
)

echo.
echo 🔄 İsim değiştiriliyor...
python rename_bot.py "%NEW_NAME%"

echo.
echo ✅ İşlem tamamlandı!
echo 📋 Sonraki adımlar:
echo 1. config.env dosyasını kontrol edin
echo 2. Gerekirse yeni bot token alın
echo 3. pip install -r requirements.txt
echo 4. Botu test edin: python main.py
echo.
pause
