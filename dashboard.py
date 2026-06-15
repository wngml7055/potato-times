import streamlit as st
import pandas as pd
import subprocess
import os
from datetime import datetime

st.set_page_config(
    page_title="Potato Times",
    layout="wide"
)

st.markdown("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 0rem;
    padding-left: 1rem;
    padding-right: 1rem;
    max-width: 100%;
}

h2,h3 {
    margin-bottom: 0.3rem;
}

[data-testid="metric-container"] {
    padding: 0.2rem;
}

[data-testid="stMetricValue"] {
    font-size: 28px;
}

</style>
""", unsafe_allow_html=True)

# =====================
# 데이터 읽기
# =====================

def auto_update():

    today = datetime.today().strftime("%Y.%m.%d")

    try:

        garak = pd.read_csv("data/garak_price.csv")

        latest = str(
            garak["INVEST_DT"].iloc[0]
        )

        if latest == today:
            return True, "최신 데이터"

    except:
        pass

    try:

        subprocess.run(
            ["python", "modules/garak.py"],
            timeout=60,
            check=True
        )

        subprocess.run(
            ["python", "modules/weather.py"],
            timeout=60,
            check=True
        )

        return True, "업데이트 완료"

    except Exception as e:

        return False, str(e)

    today = datetime.today().strftime("%Y.%m.%d")

    try:

        garak = pd.read_csv("data/garak_price.csv")

        latest = str(
            garak["INVEST_DT"].iloc[0]
        )

        if latest == today:
            return

    except:
        pass

    try:
        subprocess.run(
            ["python", "modules/garak.py"],
            timeout=60
        )
    except:
        pass

    try:
        subprocess.run(
            ["python", "modules/weather.py"],
            timeout=60
        )
    except:
        pass

success, message = auto_update()

weather = pd.read_csv("data/weather.csv")
garak = pd.read_csv("data/garak_price.csv")

st.title("🥔 POTATO TIMES")

import os

weather_icon = {
    "맑음": "assets/sunny.png",
    "구름많음": "assets/cloud.png",
    "흐림": "assets/cloudy.png",
    "비": "assets/rain.png"
}

# =====================
# 가락시장 시세
# =====================

st.subheader("가락시장 감자 시세")

cols = st.columns(4)

for idx, grade in enumerate(["특","상","보통","하"]):

    row = garak[
        garak["G_NAME"] == grade
    ].iloc[0]

    current_price = round(
        int(row["AV_P"]) / 20
    )

    last_year_price = round(
        int(
            str(row["J_365_RATE"])
            .split("(")[0]
            .replace(",","")
        ) / 20
    )

    diff_rate = round(
        (
            current_price
            - last_year_price
        )
        / last_year_price
        * 100,
        1
    )

    with cols[idx]:

        st.metric(
            grade,
            f"{current_price:,}원/kg"
        )

        st.caption(
            f"전년 {last_year_price:,}원/kg"
        )

        st.caption(
            f"▼ {abs(diff_rate)}%"
        )

st.markdown("""
<style>
[data-testid="metric-container"] {
    padding: 0.3rem 0.5rem;
}

[data-testid="metric-container"] label {
    font-size: 12px;
}

[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-size: 28px;
}

[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

st.divider()


# =====================
# 가격 추이
# =====================

left, right = st.columns([1,2])
history = pd.read_csv("data/garak_history.csv")

st.write(
    history["INVEST_DT"].min(),
    history["INVEST_DT"].max()
)

special = history[
    history["G_NAME"] == "특"
].copy()

special["INVEST_DT"] = pd.to_datetime(
    special["INVEST_DT"]
)

special = special.sort_values(
    "INVEST_DT"
)

# 최근 30일

# 최근 30일

recent30 = special.tail(30).copy()

recent30["KG_P"] = (
    recent30["AV_P"] / 20
).round(0)

# 전년 동일일 데이터 생성

last_year = special.copy()

last_year["INVEST_DT"] = (
    last_year["INVEST_DT"]
    + pd.DateOffset(years=1)
)

last_year["KG_P_LY"] = (
    last_year["AV_P"] / 20
).round(0)

# 날짜 기준 병합

chart1 = pd.merge(
    recent30[["INVEST_DT","KG_P"]],
    last_year[["INVEST_DT","KG_P_LY"]],
    on="INVEST_DT",
    how="left"
)

chart1["KG_P_LY"] = (
    chart1["KG_P_LY"]
    .interpolate()
    .bfill()
    .ffill()
)

chart1 = chart1.set_index("INVEST_DT")

# 월평균

monthly = special.copy()

monthly["월"] = monthly[
    "INVEST_DT"
].dt.strftime("%Y-%m")

monthly = (
    monthly
    .groupby("월")["AV_P"]
    .mean()
    .reset_index()
)

monthly["KG_P"] = (
    monthly["AV_P"] / 20
).round(0)

chart2 = monthly[
    ["월","KG_P"]
].set_index("월")

with left:

    st.subheader("최근 30일 특등 가격")

    st.line_chart(
        chart1,
        height=300
    )

    st.subheader("월별 평균 가격")

    st.line_chart(
        chart2,
        height=300
    )

with right:

    st.subheader("산지별 10일 예보")

    areas = [
        "양구",
        "진부",
        "보성",
        "영광",
        "당진",
        "구미"
    ]

    sample = weather[
        weather["지역"] == "양구"
    ]

    header = st.columns(len(sample)+1)

    header[0].markdown("**산지**")

    for i, (_, row) in enumerate(sample.iterrows()):

        header[i+1].markdown(
            f"**{str(row['날짜'])[5:]}**"
        )

    for area in areas:

        area_df = weather[
            weather["지역"] == area
        ]

        cols = st.columns(
             len(area_df)+1,
             gap="small" 
        )

        cols[0].markdown(
            f"**{area}**"
        )

        for i, (_, row) in enumerate(area_df.iterrows()):

            weather_text = str(
                row["오후날씨"]
            )

            icon_path = None

            for key in weather_icon:

                if key in weather_text:

                    icon_path = weather_icon[key]
                    break

            with cols[i+1]:

                if icon_path:

                    st.image(icon_path, width=55)

                st.caption(f"{row['최저기온']}~{row['최고기온']}°C")
                st.caption(f"💧 {row['오후강수확률']}")

        st.divider()