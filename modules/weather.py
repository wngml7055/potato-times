import requests
import pandas as pd
from bs4 import BeautifulSoup

REGIONS = {
    "양구": {
        "code": "5180034000",
        "lat": "38.28735327934946",
        "lon": "128.13951330237686"
    },
    "진부": {
        "code": "5176036000",
        "lat": "37.6617121732506",
        "lon": "128.578254051724"
    },
    "보성": {
        "code": "1275039000",
        "lat": "34.67118236589907",
        "lon": "127.08703042156348"
    },
    "영광": {
        "code": "1283025600",
        "lat": "35.3989165472172",
        "lon": "126.408212724498"
    },
    "당진": {
        "code": "4427036000",
        "lat": "36.84289364003771",
        "lon": "126.71351396842641"
    },
    "구미": {
        "code": "4719025000",
        "lat": "36.238335198222074",
        "lon": "128.29592387498425"
    }
}


def get_weather(region_name, region):

    url = "https://www.weather.go.kr/w/wnuri-fct2021/main/digital-forecast.do"

    params = {
        "code": region["code"],
        "unit": "m/s",
        "hr1": "N",
        "ts": "",
        "lat": region["lat"],
        "lon": region["lon"]
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.weather.go.kr/w/forecast/overall/short-term.do"
    }

    html = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=20
    ).text

    with open(
        f"{region_name}.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")

    days = soup.select(".dfs-daily-slide")[1:11]

    print("전체 slide =", len(soup.select(".dfs-daily-slide")))

    for d in soup.select(".dfs-daily-slide"):
        print(d.get("data-date"))

    print(region_name, "예보개수 =", len(days))

    result = []

    for day in days:

        try:

            date = day.get("data-date")

            weather_am_tag = day.select_one(".daily-weather-am span")
            weather_pm_tag = day.select_one(".daily-weather-pm span")

            # 중기예보(종일)
            if not weather_am_tag and not weather_pm_tag:

                allday = day.select_one(".daily-weather-allday span")

                if allday:
                    weather_am = allday.get("title", "-")
                    weather_pm = allday.get("title", "-")
                else:
                    weather_am = "-"
                    weather_pm = "-"

            else:

                weather_am = (
                    weather_am_tag.get("title", "-")
                    if weather_am_tag else "-"
                )

                weather_pm = (
                    weather_pm_tag.get("title", "-")
                    if weather_pm_tag else "-"
                )

            temps = day.select(".daily-minmax span")

            if len(temps) >= 2:
                min_temp = temps[0].text.replace("℃", "")
                max_temp = temps[1].text.replace("℃", "")
            else:
                min_temp = "-"
                max_temp = "-"

            pop_am_tag = day.select_one(".daily-pop-am span")
            pop_pm_tag = day.select_one(".daily-pop-pm span")

            # 중기예보(종일 강수확률)
            if not pop_am_tag and not pop_pm_tag:

                pop_all = day.select_one(".daily-pop-allday span")

                if pop_all:
                    pop_am = pop_all.text
                    pop_pm = pop_all.text
                else:
                    pop_am = "-"
                    pop_pm = "-"

            else:

                pop_am = pop_am_tag.text if pop_am_tag else "-"
                pop_pm = pop_pm_tag.text if pop_pm_tag else "-"

            result.append({
                "지역": region_name,
                "날짜": date,
                "오전날씨": weather_am,
                "오후날씨": weather_pm,
                "최저기온": min_temp,
                "최고기온": max_temp,
                "오전강수확률": pop_am,
                "오후강수확률": pop_pm
            })

        except Exception as e:
              print(
                   region_name,
                   date,
                   e
               )

    return result


all_data = []

for region_name, region in REGIONS.items():

    print(f"{region_name} 수집중...")

    all_data.extend(
        get_weather(region_name, region)
    )

df = pd.DataFrame(all_data)

print("\n")
print(df.head(20))

print("\n데이터크기")
print(df.shape)

print("\n지역별 건수")
print(df.groupby("지역").size())

df.to_csv(
    "data/weather.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nweather.csv 저장완료")

print(df.tail(10))
