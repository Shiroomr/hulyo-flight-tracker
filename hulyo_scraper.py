import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_hulyo_flights():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.hulyo.co.il/flights", timeout=60000)
        try:
            page.wait_for_selector(".flight-tile", timeout=15000)
        except:
            print("⚠️ .flight-tile selector not found in time", flush=True)

        # Save the actual HTML content for inspection
        html = page.content()
        with open("page_snapshot.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        print("✅ Page snapshot written", flush=True)
            
        flights = []
        # Print a snippet of the content (optional for logs)
        print(html[:1000], flush=True)
        
        # Now try to extract flight tiles
        cards = page.query_selector_all(".flight-tile")
        print(f"Found {len(cards)} flight tiles", flush=True)

        for card in cards:
            try:
                destination = card.query_selector(".destination-name").inner_text().strip()
                dates = card.query_selector(".dates").inner_text().strip()
                price = card.query_selector(".price").inner_text().strip()
                url = card.query_selector("a").get_attribute("href")

                flights.append({
                    "destination": destination,
                    "dates": dates,
                    "price": price,
                    "link": f"https://www.hulyo.co.il{url}",
                    "scraped_at": datetime.now().isoformat()
                })
            except Exception as e:
                print("Error parsing a card:", e)


        browser.close()
        return flights

def save_to_csv(flights, filename="hulyo_flights.csv"):
    df = pd.DataFrame(flights)
    df.to_csv(filename, mode='a', index=False, header=not pd.io.common.file_exists(filename))

if __name__ == "__main__":
    data = scrape_hulyo_flights()
    if data:
        save_to_csv(data)
        print(f"Scraped {len(data)} deals at {datetime.now().isoformat()}")
    else:
        print("No data scraped.")

