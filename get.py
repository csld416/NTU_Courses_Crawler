from playwright.sync_api import sync_playwright
import csv
import re
import pandas as pd

def scrape_all_terms(keyword):
    all_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()
        page.goto("https://course.ntu.edu.tw")

        # Step 1: Perform dummy search to reveal term selector
        page.fill("#id-k", keyword)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)

        # Step 2: Collect all buttons and filter the term ones manually
        buttons = page.locator("button")
        print("🧪 After search, visible buttons:")

        term_button_indices = []
        term_values = []

        for i in range(buttons.count()):
            try:
                text = buttons.nth(i).inner_text().strip()
                if re.match(r"^\d{3}-\d$", text):  # term pattern
                    print(f"✔ Found term button: {text}")
                    term_button_indices.append(i)
                    term_values.append(text)
            except:
                continue

        print(f"✅ Found {len(term_button_indices)} term buttons.")

        for idx, term_value in zip(term_button_indices, term_values):
            print(f"▶ Switching to term {term_value}...")

            try:
                buttons.nth(idx).click()
                page.wait_for_timeout(1000)

                # Refill search after switching term
                page.fill("#id-k", keyword)
                page.keyboard.press("Enter")
                page.wait_for_timeout(3000)

                # Scrape course entries
                course_items = page.locator("a.text-primary-main")
                count = course_items.count()
                print(f"   → Found {count} courses under term {term_value}")

                for j in range(count):
                    try:
                        title = course_items.nth(j).inner_text()
                        parent = course_items.nth(j).locator("xpath=../../..")
                        card_text = parent.inner_text()
                        row = [title] + card_text.split("\n") + [term_value]
                        all_data.append(row)
                    except Exception as e:
                        print(f"❌ Failed on course #{j}: {e}")
                        continue

            except Exception as e:
                print(f"❌ Failed to click term {term_value}: {e}")
                continue

    # Parse and clean
    cleaned = []
    for row in all_data:
        if len(row) < 6 or "快速搜尋" in row[0]:
            continue
        try:
            title = row[0]
            serial = re.search(r'\d{5}', ','.join(row)).group()
            code = row[2]
            classroom = row[3]
            instructor = row[4]
            time = row[5]
            term = row[-1]

            credits = re.search(r'(\d+)學分', ','.join(row))
            credits = credits.group(1) if credits else ""

            course_type = "必修" if "必修" in ','.join(row) else "選修"

            quota_match = re.search(r'(\d+)\s*人', ','.join(row))
            quota = quota_match.group(1) if quota_match else ""

            notes = ' / '.join(row[6:-1]).strip()

            cleaned.append([title, serial, code, classroom, instructor, time, credits, course_type, quota, notes, term])

        except Exception as e:
            print("❌ Failed to parse row:", row)
            print("Reason:", e)
            continue

    df = pd.DataFrame(cleaned, columns=["Title", "Serial", "Code", "Classroom", "Instructor", "Time", "Credits", "Type", "Quota", "Notes", "Term"])
    df.to_csv(f"{keyword}_multi_term_cleaned.csv", index=False, encoding="utf-8-sig")
    print("✅ Done! File saved as:", f"{keyword}_multi_term_cleaned.csv")

# Run it
scrape_all_terms("人工智慧")
