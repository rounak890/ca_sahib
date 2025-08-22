from bs4 import BeautifulSoup
import json
import requests


def comp_fetch_and_extract():
    BASE = "https://eztax.in/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Referer": BASE,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    url = "https://eztax.in/tax-compliance-calendar-it-tds-gst-roc"
    r = requests.get(url , headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    results = []

    # Find all tables with the calendar icon in the header
    for table in soup.find_all("table", class_="table-hover"):
        th = table.find("th")
        if th and th.find("i", class_="fal fa-calendar fa-lg text-secondary"):
            # Extract month and year from the header text
            header_text = th.get_text(strip=True)
            # e.g., "April 2025"
            month_year = header_text.replace('\xa0', ' ').strip()
            month, year = month_year.split()[:2]

            # Extract all rows
            for tr in table.find("tbody").find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) == 2:
                    date = tds[0].get_text(strip=True)
                    desc = tds[1].get_text(" ", strip=True)
                    results.append({
                        "month": month,
                        "year": year,
                        "date": date,
                        "description": desc
                    })

    print("Extracted", len(results), "events.")

    return results


from datetime import datetime

def is_good_compliance_date_check(date, month, year):
    curr_date = datetime.now()
    if year == curr_date.year :
        if month == curr_date.month:
            # we need to check the date now
            if date >= curr_date.day:
                return True

        elif month > curr_date.month:
            return True
    
    return False
