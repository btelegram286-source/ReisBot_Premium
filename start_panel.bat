@echo off
setlocal enabledelayedexpansion

REM ReisBot Panel - Windows başlatma betiği
REM 1) Proje dizinine geç
cd /d "%~dp0"

REM 2) Sanal ortam yoksa oluştur ve bağımlılıkları yükle
if not exist "venv\Scripts\python.exe" (
  echo [SETUP] venv olusturuluyor...
  py -3 -m venv venv
  if errorlevel 1 (
    echo [HATA] venv olusturulamadi. Python 3 kurulu mu?
    pause
    exit /b 1
  )
  echo [SETUP] pip guncelleniyor...
  call venv\Scripts\python -m pip install --upgrade pip
  echo [SETUP] paketler yukleniyor...
  call venv\Scripts\python -m pip install -r requirements.txt
)

REM 3) Port ayarla (config.env varsa oradan okunacak, aksi halde 5000)
set "PORT_FROM_ENV="
for /f "usebackq tokens=1,2 delims==" %%A in ("config.env") do (
  if /I "%%A"=="WEB_PORT" set "PORT_FROM_ENV=%%B"
)

if not defined PORT_FROM_ENV (
  set "WEB_PORT=5000"
) else (
  for /f "delims= " %%P in ("!PORT_FROM_ENV!") do set "WEB_PORT=%%P"
)

echo [INFO] ReisBot Web Panel baslatiliyor: http://localhost:%WEB_PORT%
echo [CTRL+C] ile durdurabilirsiniz.

REM 4) Paneli calistir
call venv\Scripts\python web_dashboard.py

echo.
echo [INFO] Uygulama sonlandi.
pause
