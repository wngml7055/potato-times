import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

url = "https://www.kamis.or.kr/customer/trend/trade/daily.do"

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

today = datetime.now(
    ZoneInfo("Asia/Seoul")
)

rows = []

for i in range(7):

    day = today - timedelta(days=i)

    regday = day.strftime("%Y.%m.%d")

    r = requests.get(
        url,
        params={
            "action": "list",
            "regday": regday,
            "itemcategorycode": "",
            "itemcode": "",
            "kindcode": "",
            "period": "1",
            "productclscode": "",
            "countycode": ""
        },
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=20
    )

    soup = BeautifulSoup(r.text, "html.parser")

    titles = soup.select("h3.lg_tit")

    texts = soup.select("pre.txt_box p")

    for title, text in zip(titles, texts):

        title_text = title.get_text(" ", strip=True)

        if "감자" not in title_text:
            continue

        rows.append({
            "date": regday,
            "title": title_text,
            "content": text.get_text(" ", strip=True)
        })

df = pd.DataFrame(rows)

df["title"] = (
    df["title"]
    .astype(str)
    .str.replace("\xa0", " ", regex=False)
)

df["content"] = (
    df["content"]
    .astype(str)
    .str.replace("\xa0", " ", regex=False)
)

df.to_csv(
    "data/kamis_potato.csv",
    index=False,
    encoding="utf-8-sig"
)

print(df.head())
print(f"{len(df)}건 저장 완료")
