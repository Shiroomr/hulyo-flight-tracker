import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_hulyo_flights():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(httpswww.hulyo.co.ilflights, timeout=60000)
        page.wait_for_timeout(5000)  # wait for JS to render (can tweak)

        flights = []

        cards = page.query_selector_all(".flight-tile")
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

