# SAGA Bot — автоустановщик для Windows
# Запускать: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; iex (irm "https://raw.githubusercontent.com/BizarreAsh/neverforget.ink/claude/telegram-listing-tracker-bot-t4aue/saga-bot/bootstrap.ps1")

$ErrorActionPreference = "Stop"
$dir = "$env:USERPROFILE\Desktop\SAGA-Bot"

Write-Host ""
Write-Host "  SAGA Bot — установка" -ForegroundColor Cyan
Write-Host "  ─────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""

# Создаём папку на Рабочем столе
New-Item -ItemType Directory -Force -Path $dir | Out-Null
Write-Host "  Папка: $dir" -ForegroundColor Gray

# Скачиваем файлы бота
$base = "https://raw.githubusercontent.com/BizarreAsh/neverforget.ink/claude/telegram-listing-tracker-bot-t4aue/saga-bot"
Write-Host "  Скачиваю файлы..." -ForegroundColor Gray
foreach ($f in @("bot.py", "requirements.txt", "setup_wizard.py")) {
    Invoke-WebRequest "$base/$f" -OutFile "$dir\$f" -UseBasicParsing
}
Write-Host "  ✅ Файлы получены" -ForegroundColor Green

# Проверяем Python
Write-Host ""
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "  Python не найден — открываю страницу загрузки..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Инструкция:" -ForegroundColor White
    Write-Host "  1. Скачай и установи Python с открывшейся страницы"
    Write-Host "  2. ВАЖНО: поставь галку 'Add Python to PATH'"
    Write-Host "  3. После установки запусти этот скрипт снова"
    Write-Host ""
    Start-Process "https://www.python.org/downloads/"
    Read-Host "  Нажми Enter для выхода"
    exit
}

$pyver = python --version 2>&1
Write-Host "  ✅ $pyver найден" -ForegroundColor Green

# Устанавливаем зависимости
Write-Host ""
Write-Host "  Устанавливаю зависимости (1-3 минуты)..." -ForegroundColor Gray
Set-Location $dir
pip install -q playwright aiohttp python-dotenv
Write-Host "  Устанавливаю браузер Chromium..." -ForegroundColor Gray
playwright install chromium --quiet
Write-Host "  ✅ Всё установлено" -ForegroundColor Green

# Запускаем мастер настройки
Write-Host ""
Write-Host "  ─────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  Настройка" -ForegroundColor Cyan
Write-Host "  ─────────────────────────────────────" -ForegroundColor DarkGray
python setup_wizard.py

# Создаём ярлык "Запустить бот" на Рабочем столе
$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut("$env:USERPROFILE\Desktop\▶ Запустить SAGA Bot.lnk")
$lnk.TargetPath = "cmd.exe"
$lnk.Arguments = "/k `"cd /d `"$dir`" && python bot.py`""
$lnk.WorkingDirectory = $dir
$lnk.IconLocation = "shell32.dll,24"
$lnk.Save()

Write-Host ""
Write-Host "  ─────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  Готово!" -ForegroundColor Green
Write-Host ""
Write-Host "  На Рабочем столе появился ярлык:" -ForegroundColor White
Write-Host "  '▶ Запустить SAGA Bot'" -ForegroundColor Yellow
Write-Host "  Дважды кликай по нему — бот запустится." -ForegroundColor White
Write-Host ""
Read-Host "  Нажми Enter для выхода"
