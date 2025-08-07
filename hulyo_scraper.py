from playwright.sync_api import sync_playwright
import csv
import time
from datetime import datetime
import locale

def scrape_hulyo_flights(max_flights_to_extract=100):
    extraction_date_obj = datetime.now().date()
    extraction_date_str = extraction_date_obj.strftime("%Y-%m-%d")
    extraction_weekday = extraction_date_obj.strftime("%A")

    try:
        locale.setlocale(locale.LC_TIME, 'he_IL.utf8')
    except:
        pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.hulyo.co.il/flights", timeout=60000)

        page.wait_for_selector("h3._title_vvfcu_59", timeout=30000)
        print("✅ Page loaded, destinations found", flush=True)

        page.wait_for_selector("li._root_vvfcu_1", timeout=20000)
        destinations = page.query_selector_all("li._root_vvfcu_1")
        print(f"✅ Found {len(destinations)} destinations", flush=True)

        flights = []
        flight_count = 0

        for i, dest in enumerate(destinations):
            if flight_count >= max_flights_to_extract:
                break

            try:
                destinations = page.query_selector_all("li._root_vvfcu_1")
                current_dest = destinations[i]

                destination_name_elem = current_dest.query_selector("h3._title_vvfcu_59")
                destination_name = destination_name_elem.inner_text().strip() if destination_name_elem else f"Destination {i+1}"

                current_dest.scroll_into_view_if_needed()
                time.sleep(1)
                current_dest.click()
                print(f"🛫 Clicked destination {i + 1}/{len(destinations)}: {destination_name}", flush=True)

                page.wait_for_selector("li._root_tz483_1", timeout=15000)
                date_options = page.query_selector_all("li._root_tz483_1")
                print(f"📅 Found {len(date_options)} departure dates", flush=True)

                for j, date_option in enumerate(date_options):
                    if flight_count >= max_flights_to_extract:
                        break

                    try:
                        date_options = page.query_selector_all("li._root_tz483_1")
                        current_date = date_options[j]
                        current_date.scroll_into_view_if_needed()
                        time.sleep(0.5)
                        current_date.click()
                        print(f"📆 Clicked departure date {j + 1}/{len(date_options)}", flush=True)

                        page.wait_for_selector("li._root-v2-FLIGHTS_1h6v0_21", timeout=15000)
                        flight_cards = page.query_selector_all("li._root-v2-FLIGHTS_1h6v0_21")
                        print(f"🧳 Found {len(flight_cards)} flights", flush=True)

                        for card in flight_cards:
                            if flight_count >= max_flights_to_extract:
                                break
                            try:
                                labels = card.query_selector_all("._label-v2_1h6v0_75")
                                price = card.query_selector("._price-v2_1h6v0_102").inner_text().strip()
                                currency = card.query_selector("._currency-v2-FLIGHTS_1h6v0_109").inner_text().strip()
                                departure_raw = labels[0].inner_text().strip() if labels else ""
                                return_raw = labels[1].inner_text().strip() if len(labels) > 1 else ""

                                # Parse departure date
                                try:
                                    departure_parts = departure_raw.split()
                                    departure_date_obj = datetime.strptime(departure_parts[0], "%d.%m.%y").date()
                                    departure_date_str = departure_date_obj.strftime("%Y-%m-%d")
                                    departure_weekday = departure_parts[1] if len(departure_parts) > 1 else ""
                                except:
                                    departure_date_str = departure_raw
                                    departure_weekday = ""
                                    departure_date_obj = None

                                # Parse return date
                                try:
                                    return_parts = return_raw.split()
                                    return_date_obj = datetime.strptime(return_parts[0], "%d.%m.%y").date()
                                    return_date_str = return_date_obj.strftime("%Y-%m-%d")
                                    return_weekday = return_parts[1] if len(return_parts) > 1 else ""
                                except:
                                    return_date_str = return_raw
                                    return_weekday = ""
                                    return_date_obj = None

                                # Delta days
                                try:
                                    delta_days = (departure_date_obj - extraction_date_obj).days if departure_date_obj else ""
                                except:
                                    delta_days = ""

                                flights.append({
                                    "destination_name": destination_name,
                                    "departure_date": departure_date_str,
                                    "departure_weekday": departure_weekday,
                                    "return_date": return_date_str,
                                    "return_weekday": return_weekday,
                                    "departure_time": labels[2].inner_text().strip() if len(labels) > 2 else "",
                                    "return_time": labels[3].inner_text().strip() if len(labels) > 3 else "",
                                    "price": f"{price} {currency}",
                                    "extractionDate": extraction_date_str,
                                    "extraction_weekday": extraction_weekday,
                                    "delta_days": delta_days
                                })
                                flight_count += 1
                            except Exception as e:
                                print(f"❌ Error extracting flight: {e}", flush=True)

                    except Exception as e:
                        print(f"⚠️ Error with departure date {j + 1}: {e}", flush=True)

                page.goto("https://www.hulyo.co.il/flights", timeout=60000)
                page.wait_for_selector("li._root_vvfcu_1", timeout=15000)
                time.sleep(2)

            except Exception as e:
                print(f"❌ Error with destination {i + 1}: {e}", flush=True)

        if flights:
            with open("hulyo_flights.csv", "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "destination_name",
                    "departure_date",
                    "departure_weekday",
                    "return_date",
                    "return_weekday",
                    "departure_time",
                    "return_time",
                    "price",
                    "extractionDate",
                    "extraction_weekday",
                    "delta_days"
                ])
                writer.writeheader()
                writer.writerows(flights)
            print(f"✅ {flight_count} flights saved to hulyo_flights.csv", flush=True)
        else:
            print("⚠️ No flights scraped", flush=True)

        browser.close()

if __name__ == "__main__":
    scrape_hulyo_flights(max_flights_to_extract=100)
