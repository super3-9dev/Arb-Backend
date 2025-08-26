from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from playwright.sync_api import sync_playwright
import threading
import asyncio
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared data storage
scraped_data_api = []
scraped_data_dom = []

# ---- Playwright Scraper Functions ----


def golbet724_scraper():
    global scraped_data_api
    logger.info("Starting golbet724 scraper")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto("https://www.golbet724.com/login")
            page.fill("input[type='text']", "dayı21")
            page.fill("input[type='password']", "123456")
            page.click("input[type='submit']")
            page.wait_for_selector("a[href='/maclar']")

            token = page.evaluate("() => localStorage.getItem('auth_token')")

            while True:
                try:
                    response = context.request.get(
                        "https://www.golbet724.com/api/macServis/GetMaclar/27818",
                        headers={
                            "authorization": f"Bearer {token}",
                            "referer": "https://www.golbet724.com/maclar",
                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                            "x-requested-with": "XMLHttpRequest",
                            "accept": "application/json, text/javascript, */*; q=0.01",
                        },
                    )
                    data = response.json()

                    new_items = []
                    from datetime import datetime, timezone, timedelta
                    import re

                    # Use Turkey timezone (UTC+3)
                    turkey_tz = timezone(timedelta(hours=3))
                    today = datetime.now(turkey_tz).date()
                    for game in data.get("Maclar", []):
                        baslama_utc = game.get("BaslamaTarihiUtc")
                        if not baslama_utc:
                            continue

                        # Parse ISO 8601 datetime string (e.g., "2025-08-30T14:30:00Z")
                        try:
                            # Remove 'Z' and parse the datetime
                            if baslama_utc.endswith("Z"):
                                baslama_utc = baslama_utc[:-1]
                            game_datetime = datetime.fromisoformat(baslama_utc)

                            # Convert to Turkey timezone for comparison
                            game_datetime_turkey = game_datetime.replace(
                                tzinfo=timezone.utc
                            ).astimezone(turkey_tz)
                            game_date = game_datetime_turkey.date()
                            # Only include games from today (Turkey time)
                            if game_date != today:
                                continue
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Error parsing date {baslama_utc}: {e}")
                            continue
                        team_1 = game.get("EvSahibi")
                        team_2 = game.get("Misafir")
                        scores = game.get("Oranlar")[0]
                        average = (
                            scores.get("o1", 0) + scores.get("o0", 0) + scores.get("o2", 0)
                        ) / 3
                        row_id = f"{team_1}_{team_2}"

                        new_items.append(
                            {
                                "id": row_id,
                                "team_1": team_1,
                                "team_2": team_2,
                                "average": average,
                            }
                        )

                    if new_items:
                        scraped_data_api = new_items
                        logger.info(f"Updated golbet724 data: {len(new_items)} items")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error in golbet724 scraper loop: {e}")
                    time.sleep(5)  # Wait longer on error
    except Exception as e:
        logger.error(f"Fatal error in golbet724 scraper: {e}")
        # Restart the scraper after a delay
        time.sleep(30)
        golbet724_scraper()

def orbitxch_scraper():
    global scraped_data_dom
    logger.info("Starting orbitxch scraper")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                locale="en-US",
            )
            page = context.new_page()
            page.goto("https://orbitxch.com/customer/sport/1", wait_until="networkidle")
            page.click("li.biab_tab.styles_filters__filter__a-BMo:has-text('Today')")
            page.wait_for_selector("div.biab_group-markets-table-row")

            while True:
                try:
                    all_rows = []
                    seen_ids = set()
                    last_count = 0
                    while True:
                        rows = page.query_selector_all(
                            "div.biab_group-markets-table-row.row.rowMarket.styles_row__mAQdP"
                        )

                        for row in rows:
                            # Extract the data-market-id attribute
                            market_id = row.get_attribute("data-market-id")

                            teams = row.query_selector_all(
                                "div.biab_market-title-team-names p[data-auto='runner_name']"
                            )
                            team_1 = teams[0].inner_text() if len(teams) > 0 else ""
                            team_2 = teams[1].inner_text() if len(teams) > 1 else ""

                            # buttons = row.query_selector_all("button.betContentCellMarket.biab_bet.styles_betContentCell__-gv8u.biab_bet-content-cell.biab_lay-cell.biab_lay-0.biab_bet-lay.lay-cell")
                            buttons = row.query_selector_all(
                                "span.styles_tooltip__N52t4"
                            )

                            def get_odds(button):
                                span = button.query_selector(
                                    "span.styles_betOdds__bxapE.biab_bet-odds.betOdds"
                                )
                                return span.inner_text() if span else 0

                            o1 = get_odds(buttons[1]) if len(buttons) > 0 else 0
                            o2 = get_odds(buttons[3]) if len(buttons) > 1 else 0
                            o3 = get_odds(buttons[5]) if len(buttons) > 2 else 0
                            average = (float(o1) + float(o2) + float(o3)) / 3
                            row_id = f"{team_1}_{team_2}"

                            if row_id not in seen_ids:
                                all_rows.append(
                                    {
                                        "id": row_id,
                                        "team_1": team_1,
                                        "team_2": team_2,
                                        "average": average,
                                        "market_id": market_id,  # Add the market ID to your data
                                    }
                                )
                                seen_ids.add(row_id)
                                logger.debug(
                                    f"Added row: {team_1} vs {team_2}, Market ID: {market_id}"
                                )

                        if len(all_rows) == last_count:
                            # Try auto-scroll within the scrollable container
                            finished = page.evaluate(
                                """
                                () => {
                                    const el = document.querySelector('.styles_scrollableContent__i6NQK');
                                    if (!el) return true;
                                    const before = el.scrollTop;
                                    el.scrollBy(0, 200);
                                    // If we can't scroll further, we're done
                                    if (el.scrollTop === before || el.scrollTop + el.clientHeight >= el.scrollHeight) {
                                        return true;
                                    }
                                    return false;
                                }
                                """
                            )
                            if finished:
                                logger.info(
                                    "Reached end of scrollable content, finishing data collection"
                                )
                                break
                            page.wait_for_timeout(
                                300
                            )  # Wait for content to load after scroll
                            continue

                        last_count = len(all_rows)
                        page.wait_for_timeout(
                            1000
                        )  # Reduced wait time since we're using container scrolling

                    if all_rows:
                        scraped_data_dom = all_rows
                        market_ids = [row.get("market_id", "N/A") for row in all_rows]
                        logger.info(f"Updated orbitxch data: {len(all_rows)} items")
                        logger.info(
                            f"Market IDs: {market_ids[:5]}..."
                        )  # Show first 5 market IDs
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error in orbitxch scraper loop: {e}")
                    time.sleep(5)  # Wait longer on error
    except Exception as e:
        logger.error(f"Fatal error in orbitxch scraper: {e}")
        # Restart the scraper after a delay
        time.sleep(30)
        orbitxch_scraper()

# ---- Threads to run scrapers in parallel ----
scraper_threads = []

def start_scrapers():
    global scraper_threads
    orbitxch_thread = threading.Thread(target=orbitxch_scraper, daemon=True)
    golbet724_thread = threading.Thread(target=golbet724_scraper, daemon=True)
    
    orbitxch_thread.start()
    golbet724_thread.start()
    
    scraper_threads = [orbitxch_thread, golbet724_thread]
    logger.info("Scraper threads started")

def stop_scrapers():
    logger.info("Stopping scraper threads...")
    # The daemon threads will automatically terminate when the main process ends

# Start scrapers when the application starts
start_scrapers()

# ---- REST endpoint to get current summary ----
@app.get("/summary")
def get_summary():
    # Simple summary combining both sources
    return {"api_data": scraped_data_api, "dom_data": scraped_data_dom}


# ---- WebSocket for real-time updates ----
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket client connected")
    
    try:
        while True:
            # Check if connection is still open before sending
            if websocket.client_state.value == 1:  # WebSocketState.CONNECTED
                combined = {"api_data": scraped_data_api, "dom_data": scraped_data_dom}
                await websocket.send_text(json.dumps(combined, ensure_ascii=False))
                await asyncio.sleep(5)  # push interval
            else:
                logger.info("WebSocket connection state changed, breaking loop")
                break
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected normally")
    except Exception as e:
        # Handle any other WebSocket errors gracefully
        logger.error(f"WebSocket error: {e}")
    finally:
        # Ensure connection is properly closed
        try:
            await websocket.close()
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error closing WebSocket: {e}")


if __name__ == "__main__":
    import uvicorn
    import signal
    import sys
    
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal, stopping server...")
        stop_scrapers()
        sys.exit(0)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Arb Dashboard server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
