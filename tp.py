# # import requests

# # BASE = "https://eztax.in/"

# # headers = {
# #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
# #                 "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
# #     "Referer": BASE,
# #     "Content-Type": "application/x-www-form-urlencoded"
# # }

# # url = "https://eztax.in/tax-compliance-calendar-it-tds-gst-roc"
# # r = requests.get(url , headers=headers)

# # with open('tp.html', 'w') as f:
# #     f.write(r.text)

# # from bs4 import BeautifulSoup
# # import json

# # with open("tp.html", encoding="utf-8") as f:
# #     soup = BeautifulSoup(f, "html.parser")

# # results = []

# # # Find all tables with the calendar icon in the header
# # for table in soup.find_all("table", class_="table-hover"):
# #     th = table.find("th")
# #     if th and th.find("i", class_="fal fa-calendar fa-lg text-secondary"):
# #         # Extract month and year from the header text
# #         header_text = th.get_text(strip=True)
# #         # e.g., "April 2025"
# #         month_year = header_text.replace('\xa0', ' ').strip()
# #         month, year = month_year.split()[:2]

# #         # Extract all rows
# #         for tr in table.find("tbody").find_all("tr"):
# #             tds = tr.find_all("td")
# #             if len(tds) == 2:
# #                 date = tds[0].get_text(strip=True)
# #                 desc = tds[1].get_text(" ", strip=True)
# #                 results.append({
# #                     "month": month,
# #                     "year": year,
# #                     "date": date,
# #                     "description": desc
# #                 })

# # # Output as JSON
# # with open("calendar_events.json", "w", encoding="utf-8") as out:
# #     json.dump(results, out, indent=2, ensure_ascii=False)

# # print("Extracted", len(results), "events.")

# import pandas as pd
# import json

# with open('calendar_events.json', 'r') as f:
#     d = json.load(f)

# df = pd.DataFrame(d)
# print(df.head())

# #
# import faiss

# index = faiss.read_index("vector_index.faiss")

import json
import pandas as pd


data =  {'invoice_number': '15/I12171', 
         'date': '2004-01-05', 
         'total_amount': '8.93', 
         'gst_number': None, ''
         'tds_deducted': '0.00', 
         'vendor_name': 'THE OFFICE SOLUTIONS ORGANISATION', 
         'vendor_address': 'J.Black & Partners, 9 Shakespeare Road, Wellesbourne, Stratford, Warwickshire, WK4 3VG', 
         'items': [
             {'description': 'Ref: D16352004 Sasco 2400188ar', 'quantity': '1', 'unit_price': '8.93', 'total_price': '8.93'}
             ]
        }

df = pd.DataFrame(data)
print(df)