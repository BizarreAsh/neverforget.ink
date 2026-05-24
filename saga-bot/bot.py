#!/usr/bin/env python3
"""
SAGA / immomio Telegram listing bot
Monitors immomio for new SAGA flat listings and sends Telegram alerts.

Setup:
  1. Install Python 3.11+
  2. pip install -r requirements.txt
  3. playwright install chromium
  4. cp .env.example .env  →  fill in your values
  5. python bot.py
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import aiohttp

load_dotenv()

TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
CHAT_ID: str = os.getenv("CHAT_ID", "")
TARGET_URL: str = os.getenv("TARGET_URL", "https://tenant.immomio.com/de")
CHECK_INTERVAL: int = int(os.getenv("CHECK_INTERVAL_MINUTES", "5")) * 60
SEEN_FILE = Path("seen_listings.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ── persistence ──────────────────────────────────────────────────────────────

def load_seen() -> set[str]:
    if SEEN_FILE.exists():
        try:
            return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
    return set()


def save_seen(ids: set[str]) -> None:
    SEEN_FILE.write_text(
        json.dumps(sorted(ids), ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ── telegram ──────────────────────────────────────────────────────────────────

async def send_telegram(text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, json=payload, timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    log.error(f"Telegram {resp.status}: {body[:300]}")
    except Exception as e:
        log.error(f"Telegram send error: {e}")


# ── json parser ───────────────────────────────────────────────────────────────

def _extract_from_json(data: object) -> list[dict]:
    """Flexibly extract a listing list from various JSON shapes."""
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for key in (
            "items", "results", "properties", "rentals", "units",
            "data", "content", "records", "hits", "rentalUnits",
            "publicRentals", "offers",
        ):
            val = data.get(key)
            if isinstance(val, list) and val:
                items = val
                break
        else:
            if any(k in data for k in ("id", "uid", "externalId", "propertyId")):
                items = [data]
            else:
                return []
    else:
        return []

    listings: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        item_id = str(
            item.get("id") or item.get("uid") or
            item.get("externalId") or item.get("propertyId") or ""
        )
        if not item_id:
            continue

        addr = item.get("address") or {}
        if isinstance(addr, dict):
            street = addr.get("street") or addr.get("streetName") or ""
            city = addr.get("city") or addr.get("cityName") or ""
            address = ", ".join(p for p in (street, city) if p)
        else:
            address = str(addr) if addr else ""

        title = (
            item.get("title") or item.get("name") or
            item.get("header") or address or f"ID {item_id}"
        )

        rent = (
            item.get("totalRent") or item.get("rent") or
            item.get("warmRent") or item.get("coldRent") or
            item.get("price") or ""
        )
        if isinstance(rent, (int, float)):
            rent = f"{rent:.0f}"

        item_url = (
            item.get("url") or item.get("externalUrl") or
            item.get("link") or item.get("detailUrl") or TARGET_URL
        )
        if item_url and not item_url.startswith("http"):
            item_url = "https://tenant.immomio.com" + item_url

        listings.append({
            "id": item_id,
            "title": str(title),
            "address": address,
            "rooms": str(item.get("rooms") or item.get("numberOfRooms") or item.get("roomCount") or ""),
            "area": str(item.get("area") or item.get("livingArea") or item.get("size") or ""),
            "rent": str(rent),
            "url": item_url or TARGET_URL,
        })

    return listings


# ── scraper ───────────────────────────────────────────────────────────────────

# API path fragments that suggest a property/listing endpoint
_API_KEYWORDS = (
    "rentalunit", "property", "properties", "listing", "listings",
    "rental", "wohnung", "objekt", "exposee", "flat", "apartment",
    "immobil", "search", "units", "items", "publicrent", "offer",
)


async def _dom_scrape(page, base_url: str) -> list[dict]:
    """DOM fallback: look for recognizable card elements."""
    selectors = [
        "[data-testid*='listing']", "[data-testid*='property']",
        "[class*='PropertyCard']", "[class*='ListingCard']",
        "[class*='RentalCard']", "[class*='property-card']",
        "[class*='listing-card']", "article[data-id]",
    ]
    for sel in selectors:
        elements = await page.query_selector_all(sel)
        if not elements:
            continue
        results = []
        for el in elements:
            try:
                el_id = (
                    await el.get_attribute("data-id") or
                    await el.get_attribute("data-listing-id") or
                    await el.get_attribute("id") or ""
                )
                text = (await el.inner_text()).strip()[:120]
                link_el = await el.query_selector("a[href]")
                link = (await link_el.get_attribute("href") if link_el else base_url) or base_url
                if not link.startswith("http"):
                    link = "https://tenant.immomio.com" + link
                if el_id:
                    results.append({
                        "id": el_id, "title": text, "url": link,
                        "address": "", "rooms": "", "area": "", "rent": "",
                    })
            except Exception:
                pass
        if results:
            log.info(f"DOM scrape: {len(results)} items via '{sel}'")
            return results
    return []


async def scrape(url: str) -> list[dict]:
    """Launch Playwright, intercept API responses, return deduplicated listings."""
    captured: list[dict] = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(
            locale="de-DE",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )

        async def on_response(resp):
            if resp.status != 200:
                return
            resp_url = resp.url.lower()
            if not any(k in resp_url for k in _API_KEYWORDS):
                return
            try:
                ct = resp.headers.get("content-type", "")
                if "json" not in ct:
                    return
                data = await resp.json()
                found = _extract_from_json(data)
                if found:
                    captured.extend(found)
                    log.debug(f"API hit ({len(found)} listings): {resp.url}")
            except Exception:
                pass

        page = await ctx.new_page()
        page.on("response", on_response)

        try:
            await page.goto(url, wait_until="networkidle", timeout=45_000)
        except Exception as e:
            log.warning(f"Page load warning (non-fatal): {e}")

        # Scroll to trigger lazy loaders
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(3)

        # Deduplicate by id
        seen_ids: set[str] = set()
        listings: list[dict] = []
        for item in captured:
            if item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                listings.append(item)

        if not listings:
            log.info("No API data — trying DOM fallback")
            listings = await _dom_scrape(page, url)

        await browser.close()

    return listings


# ── notification formatting ───────────────────────────────────────────────────

def _format_listing(listing: dict) -> str:
    lines = ["<b>🏠 Новая квартира SAGA!</b>"]
    lines.append(f"📍 {listing['title']}")
    if listing.get("address") and listing["address"] != listing["title"]:
        lines.append(f"🗺 {listing['address']}")
    if listing.get("rooms"):
        lines.append(f"🛏 Комнат: {listing['rooms']}")
    if listing.get("area"):
        lines.append(f"📐 Площадь: {listing['area']} м²")
    if listing.get("rent"):
        lines.append(f"💶 Аренда: {listing['rent']} €/мес")
    lines.append(f'🔗 <a href="{listing["url"]}">Смотреть объявление</a>')
    return "\n".join(lines)


# ── main loop ────────────────────────────────────────────────────────────────

async def check_once() -> None:
    seen = load_seen()
    listings = await scrape(TARGET_URL)

    if not listings:
        log.warning("No listings found — site may require login or changed structure")
        return

    log.info(f"Fetched {len(listings)} listings total")

    first_run = not SEEN_FILE.exists()
    if first_run:
        save_seen({l["id"] for l in listings})
        log.info(f"First run: saved {len(listings)} existing listings, watching for new ones")
        await send_telegram(
            f"✅ <b>SAGA бот запущен!</b>\n"
            f"Слежу за: {TARGET_URL}\n"
            f"Сейчас {len(listings)} объявлений — пришлю уведомление о новых."
        )
        return

    new = [l for l in listings if l["id"] not in seen]
    for listing in new:
        await send_telegram(_format_listing(listing))
        seen.add(listing["id"])
        log.info(f"  → Notified: {listing['id']} — {listing['title']}")

    if new:
        save_seen(seen)
        log.info(f"Sent {len(new)} notification(s)")
    else:
        log.info("No new listings this round")


async def main() -> None:
    log.info("=" * 55)
    log.info("SAGA listing bot starting")
    log.info(f"Target : {TARGET_URL}")
    log.info(f"Interval: {CHECK_INTERVAL // 60} min")
    log.info("=" * 55)

    if not TELEGRAM_TOKEN:
        log.error("TELEGRAM_TOKEN not set — edit .env and restart")
        return
    if not CHAT_ID:
        log.error("CHAT_ID not set — edit .env and restart")
        return

    while True:
        try:
            await check_once()
        except Exception as e:
            log.error(f"Unexpected error: {e}", exc_info=True)
        log.info(f"Next check in {CHECK_INTERVAL // 60} min …")
        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
