@echo off
chcp 65001 >nul
title SAGA Bot — Работает

:: Проверка конфига
if not exist .env (
    echo.
    echo  Конфиг не найден — запусти install.bat сначала!
    echo.
    pause
    exit /b 1
)

echo.
echo  ┌─────────────────────────────────────┐
echo  │   SAGA Bot запущен                  │
echo  │   Не закрывай это окно!             │
echo  └─────────────────────────────────────┘
echo.

python bot.py

echo.
echo  Бот остановлен.
pause
