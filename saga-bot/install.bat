@echo off
chcp 65001 >nul
title SAGA Bot — Установка

echo.
echo  ┌─────────────────────────────────────┐
echo  │   SAGA Bot — Первичная установка    │
echo  └─────────────────────────────────────┘
echo.

:: Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  ❌ Python не найден.
    echo.
    echo  Нужно установить Python:
    echo  1. Открою страницу загрузки...
    echo  2. Скачай и запусти установщик
    echo  3. ОБЯЗАТЕЛЬНО поставь галку "Add Python to PATH"
    echo  4. После установки запусти install.bat снова
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

echo  ✅ Python найден
echo.
echo  Устанавливаю зависимости (может занять 1-2 минуты)...
pip install -q playwright aiohttp python-dotenv
echo  Устанавливаю браузер Chromium...
playwright install chromium --quiet
echo.
echo  ✅ Зависимости установлены
echo.
echo  ─────────────────────────────────────
echo  Настройка бота
echo  ─────────────────────────────────────
echo.
python setup_wizard.py
