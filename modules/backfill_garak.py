import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

url = "https://db.garak.co.kr:9443/api/datasources/40f2c32edec68ae89c0994c0f2d8dab6"

headers = {
    "Content-Type": "application/json",

    "Dashboard-Token": "9D4EBB9B3B9AF6176EF913F22BBDACB0F545DB9D569B1499244944825CF0540E68532E26C6991DC0C5C28242479B53244A5E9893BB8CFB159984EB6E5DE2D519",

    "Share-Token": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJqdGkiOiI0YjI5ZWQ5MDcxNmIzN2Q3Yjk5ZWFjZTRkMjk1ODNlOSIsImlzcyI6IkJJWDUtU0VSVkVSIiwic3ViIjoiaHAiLCJ1c2Vybm8iOjQxLCJncm91cHMiOiI5NDc5Mjk3QTczN0YzOUJFM0Y3QTVGQjA4MjI1OUE2QSIsInJvbGVzIjoiNzQ2M0Q3OEYxOEI3NURCQUM3QUVGQ0Y1NzE3M0ZCRDBBOTIyMTg4MkYyODBCRUMyOEE2RTAxRDE1RUEzMEM1NSIsIm5hbWUiOiIwMjY1MDJCNDY2QjE1Nzc2OTFCNzE0MzU1RkI2MDIwQSIsImNjIjoiIiwidHlwZSI6IlNIQVJFIiwiZXhwIjoyNTMyMzQ0NTk3ODR9.3oTXYKHVwsLgUhAalv2VXEUzl15wBKNhbG8godeg8c7I51sQcaHNFyC4ZObIFC1dcZMT4wXRSIn3_ZtWDaWFbA",

    "Origin": "https://db.garak.co.kr:9443"
}

cookies = {
    "JSESSIONID": "JSESSIONID=J5J7XG9Q13dsYsevenU8qSD584e6hxVFL1NWy1MKozaSgc2tT1mOIDjpV18wiVaz.amV1c19kb21haW4veW91dG9uZw==; JSESSIONID=F95493F34A7DF052092213B33F4B67CA"
}

start_date = datetime(2020, 1, 1)
end_date = datetime.today()

all_data = []

current = start_date

while current <= end_date:

    day = current.strftime("%Y%m%d")

    print(day)

    payload = {
        "mrktDiv": "1",
        "startDate": day,
        "endDate": day,
        "handlClsCd": "2",
        "selectedItmCd": "15200",
        "selectedRptvItmCd": "15200",
        "selectedItmNm": ""
    }

    try:

        r = requests.post(
            url,
            json=payload,
            headers=headers,
            cookies=cookies,
            timeout=30
        )

        result = r.json()

        if "dataset" in result:

            data = result["dataset"]

            if len(data) > 0:
                all_data.extend(data)

    except Exception as e:

        print("오류:", day, e)

    current += timedelta(days=1)

    time.sleep(0.3)

df = pd.DataFrame(all_data)

os.makedirs("data", exist_ok=True)

df.to_csv(
    "data/garak_history.csv",
    index=False,
    encoding="utf-8-sig"
)

print()
print("완료")
print(len(df))