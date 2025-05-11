import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://nol.ntu.edu.tw/nol/coursesearch/search_result.php"

# All academic terms
TERMS = [
    "113-2",
    "113-1",
    "112-2",
    "112-1",
    "111-2",
    "111-1",
    "110-2",
    "110-1",
    "109-2",
    "109-1",
    "108-2",
    "108-1",
    "107-2",
    "107-1",
    "106-2",
    "106-1",
    "105-2",
    "105-1",
    "104-2",
    "104-1",
    "103-2",
    "103-1",
    "102-2",
    "102-1",
    "101-2",
    "101-1",
    "100-2",
    "100-1",
    "99-2",
    "99-1",
    "98-2",
    "98-1",
    "97-2",
    "97-1",
    "96-2",
    "96-1",
    "95-2",
    "95-1",
    "94-2",
    "94-1",
    "93-2",
    "93-1",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
}


def fetch_courses(term, keyword):
    params = {
        "current_sem": term,
        "cstype": "1",
        "csname": keyword,
        "alltime": "yes",
        "allproced": "yes",
        "allsel": "yes",
        "page_cnt": 2000,
        "Submit22": "查詢",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
    }

    try:
        response = requests.get(
            BASE_URL, params=params, headers=headers, verify=False, timeout=10
        )
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("tr", align="center")[1:]  # Skip table header

        data = []
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 5:
                continue
            serial = cells[0].text.strip()
            title = cells[4].text.strip()
            if not serial.isdigit() or not title:
                continue

            department = cells[1].text.strip()
            code = cells[2].text.strip()
            class_no = cells[3].text.strip()
            credits = cells[6].text.strip()
            course_id = cells[7].text.strip()
            duration = cells[8].text.strip()
            course_type = cells[9].text.strip()
            instructor = cells[10].text.strip()
            group = cells[11].text.strip()
            time_info = cells[12].text.strip()
            quota = cells[13].text.strip()
            remarks = cells[14].text.strip()
            prereqs = cells[15].text.strip() if len(cells) > 15 else ""

            data.append(
                [
                    term,
                    serial,
                    department,
                    code,
                    class_no,
                    title,
                    credits,
                    course_id,
                    duration,
                    course_type,
                    instructor,
                    group,
                    time_info,
                    quota,
                    remarks,
                    prereqs,
                ]
            )

        return data

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error while fetching {term}: {e}")
        return []


def main():
    keyword = "強化學習"
    all_data = []

    for term in TERMS:
        print(f"🔍 Searching {term}...")
        courses = fetch_courses(term, keyword)
        print(f"   → {len(courses)} courses found.")
        all_data.extend(courses)
        time.sleep(1)  # polite pause

    df = pd.DataFrame(
        all_data,
        columns=[
            "Term",
            "Serial",
            "Department",
            "Code",
            "ClassNo",
            "Title",
            "Credits",
            "CourseID",
            "Duration",
            "Type",
            "Instructor",
            "Group",
            "Time",
            "Quota",
            "Remarks",
            "Prerequisites",
        ],
    )

    df.to_csv(f"{keyword}_ntu_courses.csv", index=False, encoding="utf-8-sig")
    print(f"✅ Done! Saved as {keyword}_ntu_courses.csv")


if __name__ == "__main__":
    main()
