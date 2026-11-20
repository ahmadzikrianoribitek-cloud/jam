@echo off
cd /d "%~dp0"
set PY=python
where py >nul 2>nul && set PY=py

%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Python belum terpasang. Pasang dari python.org dan centang "Add Python to PATH".
  pause
  exit /b
)

%PY% -m pip install psutil -q
if errorlevel 1 (
  echo Gagal memasang psutil. Pastikan komputer terhubung ke internet.
  pause
  exit /b
)

start "Netmon" /min %PY% netmon.py
echo Netmon dijalankan di jendela kecil di taskbar. Jendela ini boleh ditutup.
timeout /t 3 >nul
