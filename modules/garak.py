import requests
import pandas as pd
import os
from datetime import datetime

target_data = datetime.today().strftime("%Y%m%d")

url = "https://db.garak.co.kr:9443/api/datasources/40f2c32edec68ae89c0994c0f2d8dab6"

payload = {
    "mrktDiv": "1",
    "startDate": target_data,
    "endDate": target_data,
    "handlClsCd": "2",
    "selectedItmCd": "15200",
    "selectedRptvItmCd": "15200",
    "selectedItmNm": ""
}

headers = {
    "Content-Type": "application/json",

    "Dashboard-Token": "9D4EBB9B3B9AF6176EF913F22BBDACB0F545DB9D569B1499244944825CF0540E68532E26C6991DC0C5C28242479B53244A5E9893BB8CFB159984EB6E5DE2D519",

    "Share-Token": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJqdGkiOiI0YjI5ZWQ5MDcxNmIzN2Q3Yjk5ZWFjZTRkMjk1ODNlOSIsImlzcyI6IkJJWDUtU0VSVkVSIiwic3ViIjoiaHAiLCJ1c2Vybm8iOjQxLCJncm91cHMiOiI5NDc5Mjk3QTczN0YzOUJFM0Y3QTVGQjA4MjI1OUE2QSIsInJvbGVzIjoiNzQ2M0Q3OEYxOEI3NURCQUM3QUVGQ0Y1NzE3M0ZCRDBBOTIyMTg4MkYyODBCRUMyOEE2RTAxRDE1RUEzMEM1NSIsIm5hbWUiOiIwMjY1MDJCNDY2QjE1Nzc2OTFCNzE0MzU1RkI2MDIwQSIsImNjIjoiIiwidHlwZSI6IlNIQVJFIiwiZXhwIjoyNTMyMzQ0NTk3ODR9.3oTXYKHVwsLgUhAalv2VXEUzl15wBKNhbG8godeg8c7I51sQcaHNFyC4ZObIFC1dcZMT4wXRSIn3_ZtWDaWFbA",

    "Origin": "https://db.garak.co.kr:9443"
}

cookies = {
    "JSESSIONID": "JSESSIONID=J5J7XG9Q13dsYsevenU8qSD584e6hxVFL1NWy1MKozaSgc2tT1mOIDjpV18wiVaz.amV1c19kb21haW4veW91dG9uZw==; JSESSIONID=F95493F34A7DF052092213B33F4B67CA"
}

r = requests.post(
    url,
    json=payload,
    headers=headers,
    cookies=cookies
)

data = r.json()["dataset"]

df = pd.DataFrame(data)

if len(df) == 0:

    raise Exception(
        "가락시장 API 데이터 없음"
    )

# 오늘 데이터 저장
df.to_csv(
    "data/garak_price.csv",
    index=False,
    encoding="utf-8-sig"
)

# 이력 누적 저장
history_file = "data/garak_history.csv"

if os.path.exists(history_file):

    old = pd.read_csv(history_file)

    old["GRADE_CD"] = old["GRADE_CD"].astype(str)
    df["GRADE_CD"] = df["GRADE_CD"].astype(str)

    merged = pd.concat(
        [old, df],
        ignore_index=True
    )

    merged = merged.drop_duplicates(
        subset=["INVEST_DT", "GRADE_CD"],
        keep="last"
    )

else:

    merged = df.copy()

merged.to_csv(
    history_file,
    index=False,
    encoding="utf-8-sig"
)

print("저장 완료")

print(
    merged[
        ["INVEST_DT", "G_NAME", "AV_P"]
    ]
)