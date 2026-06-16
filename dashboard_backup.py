import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import subprocess
import os
import json
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

.title-main {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 42px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #22304A;

    margin-top: 15px;
    padding-top: 10px;
    line-height: 1.3;
}

.section-title {
    background-color: #FFF7E6;
    border-left: 5px solid #D97706;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 10px;
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

        subprocess.run(
            ["python", "modules/kamis.py"],
            timeout=30,
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

header_left, header_right = st.columns([4,1])

with header_left:

    st.markdown(
        """
        <div class='title-main'>
        🥔 POTATO TIMES
        </div>
        """,
        unsafe_allow_html=True
    )

with header_right:

    status_color = "#DFF5E1" if success else "#FFE2E2"

    status_text = "정상" if success else "오류"

    st.markdown(
        f"""
        <div style="
            background:{status_color};
            padding:10px;
            border-radius:10px;
            text-align:center;
            margin-top:20px;
        ">
            <b>● {status_text}</b><br>
            {datetime.today().strftime("%Y-%m-%d")}
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    "<hr style='margin-top:5px; margin-bottom:15px;'>",
    unsafe_allow_html=True
)

# =========================
# KAMIS 시장동향
# =========================

try:

    kamis = pd.read_csv(
        "data/kamis_potato.csv",
        encoding="cp949"
    )

    latest = kamis.iloc[0]

    st.markdown(
        f"""
        <div style="
        background:#EEF5FF;
        border-left:4px solid #4A90E2;
        padding:10px 12px;
        border-radius:6px;
        margin-bottom:12px;
        ">

        <div style="
        font-size:13px;
        font-weight:700;
        color:#1E5AA8;
        margin-bottom:4px;
        ">
        📢 KAMIS 시장동향 |
        {latest["title"]}
        </div>

        <div style="
        font-size:12px;
        color:#444;
        line-height:1.6;
        ">
        {latest["content"]}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

except Exception as e:

    st.error(f"KAMIS 오류 : {e}")

import os

weather_icon = {
    "맑음": "assets/sunny.png",
    "구름많음": "assets/cloud.png",
    "흐림": "assets/cloudy.png",
    "비": "assets/rain.png",
    "소나기": "assets/rain.png"
}

# =====================
# 가락시장 시세
# =====================

st.markdown("""
<style>

[data-testid="metric-container"]{
    padding:0rem !important;
}

[data-testid="stMetricValue"]{
    font-size:24px !important;
}

[data-testid="metric-container"] label{
    font-size:11px !important;
}

</style>
""", unsafe_allow_html=True)


# =====================
# 가격 추이
# =====================

left, right = st.columns([1,2])

with left:

    st.markdown(
        "<div class='section-title'>🥔 가락시장 감자 시세</div>",
        unsafe_allow_html=True
    )

    price_cols = st.columns(4)



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

        with price_cols[idx]:

            st.metric(
                grade,
                f"{current_price:,}"
            )

            st.caption(
                f"전년 {last_year_price:,}"
            )

            if diff_rate > 0:
                st.markdown(
                    f"<span style='color:blue'>▲ {diff_rate}%</span>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<span style='color:red'>▼ {abs(diff_rate)}%</span>",
                    unsafe_allow_html=True
                )

history = pd.read_csv("data/garak_history.csv")

normal = history[
    history["G_NAME"] == "보통"
].copy()

normal["INVEST_DT"] = pd.to_datetime(
    normal["INVEST_DT"]
)

normal = normal.sort_values(
    "INVEST_DT"
)

normal["YEAR"] = (
    normal["INVEST_DT"].dt.year
)

normal["MMDD"] = (
    normal["INVEST_DT"].dt.strftime("%m-%d")
)

normal["KG_P"] = (
    normal["AV_P"] / 20
).round(0)

today_year = datetime.today().year

# 최근 30일 날짜

recent_mmdd = (
    normal[
        normal["YEAR"] == today_year
    ]
    .sort_values("INVEST_DT")
    .tail(30)["MMDD"]
    .tolist()
)

# 평년

avg_df = (
    normal[
        normal["YEAR"].between(2020, 2025)
    ]
    .groupby("MMDD")["KG_P"]
    .mean()
    .reset_index()
)

avg_df.columns = [
    "MMDD",
    "평년"
]

# 전년

last_df = (
    normal[
        normal["YEAR"] == 2025
    ][["MMDD","KG_P"]]
)

last_df.columns = [
    "MMDD",
    "전년"
]

# 올해

this_df = (
    normal[
        normal["YEAR"] == today_year
    ][["MMDD","KG_P"]]
)

this_df.columns = [
    "MMDD",
    f"{today_year}년"
]

# 최근30일 기준 병합

chart1 = pd.DataFrame({
    "MMDD": recent_mmdd
})

chart1 = chart1.merge(
    avg_df,
    on="MMDD",
    how="left"
)

chart1 = chart1.merge(
    last_df,
    on="MMDD",
    how="left"
)

chart1 = chart1.merge(
    this_df,
    on="MMDD",
    how="left"
)

text_values = [
    str(int(v)) if i % 2 == 0 else ""
    for i, v in enumerate(
        chart1[f"{today_year}년"]
    )
]

chart1["전년"] = (
    chart1["전년"]
    .interpolate()
    .bfill()
    .ffill()
)

# 월평균

monthly = normal.copy()

monthly["MONTH"] = monthly["INVEST_DT"].dt.month

monthly_avg = (
    monthly[
        monthly["YEAR"].between(2020, 2025)
    ]
    .groupby("MONTH")["KG_P"]
    .mean()
    .reset_index()
)

monthly_last = (
    monthly[
        monthly["YEAR"] == 2025
    ]
    .groupby("MONTH")["KG_P"]
    .mean()
    .reset_index()
)

monthly_this = (
    monthly[
        monthly["YEAR"] == today_year
    ]
    .groupby("MONTH")["KG_P"]
    .mean()
    .reset_index()
)

with left:

    st.markdown(
        "<div class='section-title'>📈 최근 30일 보통가격</div>",
        unsafe_allow_html=True
    )

    fig1 = go.Figure()

    fig1.add_trace(
        go.Scatter(
            x=list(range(len(chart1))),
            y=chart1["평년"],
            name="평년",
            mode="lines",
            line=dict(
                color="gray",
                width=2
            )
        )
    )

    fig1.add_trace(
        go.Scatter(
            x=list(range(len(chart1))),
            y=chart1["전년"],
            name="전년",
            mode="lines",
            line=dict(
                color="lightblue",
                width=2
            )
        )
    )

    fig1.add_trace(
        go.Scatter(
            x=list(range(len(chart1))),
            y=chart1[f"{today_year}년"],
            name=f"{today_year}년",
            mode="lines+markers+text",
            line=dict(
                color="blue",
                width=4
            ),
            text=text_values,
            textposition="top center",
            textfont=dict(
                color="blue",
                size=10
            )
        )
    )

    fig1.update_layout(
        height=300,
        margin=dict(
            t=20,
            b=20,
            l=20,
            r=20
        ),
        legend=dict(
            orientation="h",
            y=1.15,
            x=0
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(chart1))),
            ticktext=chart1["MMDD"]
        )
    )

    st.write(fig1)

    st.plotly_chart(
        fig1,
        use_container_width=False
    )



    st.markdown(
        "<div class='section-title'>📊 월별 평균 가격</div>",
        unsafe_allow_html=True
    )

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=monthly_avg["MONTH"],
            y=monthly_avg["KG_P"],
            name="평년",
            line=dict(
                color="gray"
            )
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=monthly_avg["MONTH"],
            y=monthly_last["KG_P"],
            name="전년",
            line=dict(
                color="lightblue"
            )
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=monthly_avg["MONTH"],
            y=monthly_this["KG_P"],
            name=f"{today_year}년",
            line=dict(
                color="blue",
                width=4
            )
        )
    )

    fig2.update_layout(
        height=200,
        margin=dict(
            t=20,
            b=20,
            l=20,
            r=20
        ),
        legend=dict(
            orientation="h",
            y=1.15,
            x=0
        )
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

with right:

    st.markdown(
        "<div class='section-title'>🌤️ 산지별 10일 예보</div>",
        unsafe_allow_html=True
    )

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

            if "소나기" in weather_text:
                icon_path = "assets/rain.png"

            for key in weather_icon:

                if key in weather_text:

                    icon_path = weather_icon[key]
                    break

            with cols[i+1]:

                if icon_path:

                    st.image(icon_path, width=55)

                if "소나기" in weather_text:

                    st.markdown(
                        """
                        <div style="
                            color:#1E88E5;
                            font-size:11px;
                            font-weight:bold;
                            text-align:left;
                            margin-top:-8px;
                            margin-bottom:-4px;
                        ">
                        소나기
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(
                    f"<div style='font-size:12px; margin-top:-15px; margin-bottom:-15px;'>"
                    f"{row['최저기온']}~{row['최고기온']}°C"
                    f"</div>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<div style='font-size:12px; margin-top:-10px; margin-bottom:-20px;'>"
                    f"💧 {row['오후강수확률']}"
                    f"</div>",
                    unsafe_allow_html=True
                )

        st.markdown(
            "<hr style='margin-top:10px; margin-bottom:10px;'>",
            unsafe_allow_html=True
        )