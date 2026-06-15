import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Potato Times",
    layout="wide"
)

st.title("🥔 POTATO TIMES")

df = pd.read_csv(
    "data/weather.csv",
    encoding="utf-8-sig"
)

regions = [
    "양구",
    "진부",
    "보성",
    "영광",
    "당진",
    "구미"
]

st.markdown("## 중단기 기상정보")

col1, col2 = st.columns(2)

for idx, region in enumerate(regions):

    region_df = df[df["지역"] == region].copy()

    region_df["날짜"] = pd.to_datetime(
        region_df["날짜"]
    ).dt.strftime("%m/%d")

    weather_row = ["날씨"]
    max_row = ["최고"]
    min_row = ["최저"]
    rain_row = ["강수"]

    for _, row in region_df.iterrows():

        weather_row.append(
            row["오후날씨"]
            .replace("오후 날씨 ", "")
            .replace("오전 날씨 ", "")
        )

        max_row.append(f"{row['최고기온']}°")
        min_row.append(f"{row['최저기온']}°")

        rain_row.append(
            str(row["오후강수확률"])
        )

    display = pd.DataFrame(
        [
            weather_row,
            max_row,
            min_row,
            rain_row
        ],
        columns=[
            ""
        ] + region_df["날짜"].tolist()
    )

    target = col1 if idx % 2 == 0 else col2

    with target:

        st.markdown(f"### {region}")

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )