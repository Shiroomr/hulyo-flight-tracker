from playwright.sync_api import sync_playwright
import csv
import time

def scrape_hulyo_flights():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.hulyo.co.il/flights", timeout=60000)

        # Wait for the page to load and JS to hydrate content
        page.wait_for_load_state("networkidle", timeout=30000)  # waits until no network requests for 500ms
        
        # Optional: give the JS framework a bit of extra time to render
        time.sleep(5)
        
        # Then wait for the destination thumbnails to appear
        page.wait_for_selector(".destination-name", timeout=20000)

        destination_cards = page.query_selector_all(".destination-name")
        print(f"Found {len(destination_cards)} destination tiles", flush=True)

        flights = []

        for i, dest in enumerate(destination_cards):
            try:
                # Re-query because the DOM gets refreshed each time
                destination_cards = page.query_selector_all(".destination-name")
                current_dest = destination_cards[i]

                # Scroll into view and click
                current_dest.scroll_into_view_if_needed()
                time.sleep(0.5)
                current_dest.click()
                print(f"🛫 Clicked destination {i + 1}/{len(destination_cards)}", flush=True)

                # Wait for flight tiles to appear
                try:
                    page.wait_for_selector(".flight-tile", timeout=15000)
                except:
                    print(f"⚠️ No .flight-tile found for destination {i + 1}", flush=True)
                    continue

                # Snapshot for debug
                with open(f"page_snapshot_{i+1}.html", "w", encoding="utf-8") as f:
                    f.write(page.content())

                cards = page.query_selector_all(".flight-tile")
                print(f"🧳 Found {len(cards)} flights for destination {i + 1}", flush=True)

                for card in cards:
                    try:
                        destination = card.query_selector(".destination-name").inner_text().strip()
                        dates = card.query_selector(".flight-dates").inner_text().strip()
                        price = card.query_selector(".price").inner_text().strip()

                        flights.append({
                            "destination": destination,
                            "dates": dates,
                            "price": price
                        })
                    except Exception as e:
                        print(f"❌ Error extracting card: {e}", flush=True)

                # Click "Back" if needed (or reload the page)
                page.goto("https://www.hulyo.co.il/flights", timeout=60000)
                page.wait_for_selector(".destination-name", timeout=15000)

            except Exception as e:
                print(f"❌ Error with destination {i + 1}: {e}", flush=True)

        if flights:
            with open("hulyo_flights.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["destination", "dates", "price"])
                writer.writeheader()
                writer.writerows(flights)
            print("✅ All flights saved to hulyo_flights.csv", flush=True)
        else:
            print("⚠️ No flights scraped", flush=True)

        browser.close()

if __name__ == "__main__":
    scrape_hulyo_flights()
