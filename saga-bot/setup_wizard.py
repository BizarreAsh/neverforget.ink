#!/usr/bin/env python3
"""Interactive first-time configuration wizard."""
import os
import sys
import json
from pathlib import Path

ENV_FILE = Path(__file__).parent / ".env"


def ask(prompt: str, default: str = "") -> str:
    if default:
        val = input(f"  {prompt} [{default}]: ").strip()
        return val if val else default
    while True:
        val = input(f"  {prompt}: ").strip()
        if val:
            return val
        print("  ⚠  Не может быть пустым, попробуй ещё раз.")


def verify_telegram(token: str, chat_id: str) -> bool:
    """Quick check that token + chat_id are valid."""
    try:
        import urllib.request, json as _json
        url = f"https://api.telegram.org/bot{token}/getMe"
        with urllib.request.urlopen(url, timeout=8) as r:
            data = _json.loads(r.read())
        if not data.get("ok"):
            return False
        # Try sending a test message
        url2 = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = json.dumps({
            "chat_id": chat_id,
            "text": "✅ SAGA бот подключён и готов к работе!",
        }).encode()
        req = urllib.request.Request(url2, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as r:
            resp = _json.loads(r.read())
        return resp.get("ok", False)
    except Exception as e:
        print(f"  ⚠  Ошибка проверки: {e}")
        return False


def main():
    print()
    print(" ┌──────────────────────────────────────────┐")
    print(" │  Шаг 1 — Telegram бот                    │")
    print(" └──────────────────────────────────────────┘")
    print()
    print("  Создай бота:")
    print("  1. Открой Telegram, найди @BotFather")
    print("  2. Напиши /newbot → придумай имя → скопируй токен")
    print()

    token = ask("Вставь токен бота")

    print()
    print(" ┌──────────────────────────────────────────┐")
    print(" │  Шаг 2 — Куда слать уведомления          │")
    print(" └──────────────────────────────────────────┘")
    print()
    print("  Узнай свой Chat ID:")
    print("  → Найди @userinfobot в Telegram, напиши ему что угодно")
    print("  → Он ответит твоим Id (просто цифры, например 123456789)")
    print()
    print("  Или создай канал/группу:")
    print("  → Добавь своего бота туда как admin")
    print("  → Chat ID будет вида -1001234567890")
    print()

    chat_id = ask("Вставь Chat ID")

    print()
    print(" ┌──────────────────────────────────────────┐")
    print(" │  Шаг 3 — Ссылка на квартиры SAGA         │")
    print(" └──────────────────────────────────────────┘")
    print()
    print("  Открой в браузере страницу со списком квартир SAGA,")
    print("  примени нужные фильтры и скопируй URL из адресной строки.")
    print()

    url = ask("URL страницы", "https://tenant.immomio.com/de")

    print()
    print(" ┌──────────────────────────────────────────┐")
    print(" │  Шаг 4 — Интервал проверки               │")
    print(" └──────────────────────────────────────────┘")
    print()

    interval = ask("Проверять каждые N минут", "5")
    if not interval.isdigit():
        interval = "5"

    print()
    print("  Проверяю подключение к Telegram…")
    ok = verify_telegram(token, chat_id)
    if ok:
        print("  ✅ Успешно! Тестовое сообщение отправлено.")
    else:
        print("  ⚠  Не удалось проверить — проверь токен и Chat ID.")
        print("     Можно продолжить, но уведомления могут не приходить.")

    ENV_FILE.write_text(
        f"TELEGRAM_TOKEN={token}\n"
        f"CHAT_ID={chat_id}\n"
        f"TARGET_URL={url}\n"
        f"CHECK_INTERVAL_MINUTES={interval}\n",
        encoding="utf-8",
    )

    print()
    print("  ✅ Конфиг сохранён!")
    print()
    print("  ─────────────────────────────────────────")
    print("  Всё готово! Запускай start.bat")
    print("  ─────────────────────────────────────────")
    print()
    input("  Нажми Enter для выхода…")


if __name__ == "__main__":
    main()
