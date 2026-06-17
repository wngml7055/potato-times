import streamlit as st
is_mobile = st.query_params.get("mobile", "0") == "1"
import pandas as pd
import subprocess
import plotly.graph_objects as go
import streamlit.components.v1 as components
import os
from datetime import datetime


st.set_page_config(
    page_title="Potato Times",
    layout="wide"
)

st.markdown("""
<style>

.block-container {
    max-width: 98% !important;
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

    today = datetime.today().strftime(
        "%Y.%m.%d"
    )

    try:

        garak = pd.read_csv(
            "data/garak_price.csv"
        )

        latest = str(
            garak["INVEST_DT"].iloc[0]
        )

        if latest == today:

            return (
                True,
                "최신 데이터"
            )

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
            timeout=60,
            check=True
        )

        return (
            True,
            "업데이트 완료"
        )

    except Exception as e:

        return (
            False,
            str(e)
        )

success = True
message = "자동 업데이트 사용"

weather = pd.read_csv("data/weather.csv")

if os.path.getsize(
    "data/garak_price.csv"
) > 100:

    garak = pd.read_csv(
        "data/garak_price.csv"
    )

else:

    history_temp = pd.read_csv(
        "data/garak_history.csv"
    )

    latest_day = (
        history_temp["INVEST_DT"]
        .max()
    )

    garak = history_temp[
        history_temp["INVEST_DT"]
        == latest_day
    ].copy()

header_left, header_right = st.columns([8,1])

with header_left:

    st.markdown(
        "# 🥔 POTATO TIMES"
    )

    st.markdown(
        """
        <hr style="
            margin-top:0px;
            margin-bottom:0px;
            border:none;
            border-top:3px solid #D9D9D9;
        ">
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    <style>

    h1{
        color:#203864 !important;
        font-family:Georgia !important;
        font-weight:700 !important;
    }

</style>
""", unsafe_allow_html=True)

with header_right:

    status_color = "#DFF5E1" if success else "#FFE2E2"

    status_text = "정상" if success else "오류"

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style="
            background:{status_color};
            padding:5px;
            border-radius:5px;
            text-align:center;
        ">
            <b>● {status_text}</b><br>
            {datetime.today().strftime("%Y-%m-%d")}
        </div>
        """,
        unsafe_allow_html=True
    )

# ======================
# KAMIS 시장동향
# ======================

if os.path.exists("data/kamis_potato.csv"):

    kamis = pd.read_csv(
        "data/kamis_potato.csv",
        encoding="cp949"
    )

    if len(kamis) > 0:

        latest = kamis.iloc[0]

        title = str(
            latest["title"]
        )

        summary = str(
            latest["content"]
        )

        st.markdown(
            f"""
<div style="background:#EDF4FF;border-left:4px solid #4A90E2;padding:10px 14px;border-radius:6px;margin-top:0px;margin-bottom:0px;">
<b style="color:#1f4f9c;">📢 KAMIS 시장동향 | {title}</b>
<br>
<span style="color:#444;">{summary}</span>
</div>
            """,
            unsafe_allow_html=True
        )

# =======================


import os

weather_icon = {
    "맑음": "assets/sunny.png",
    "구름많음": "assets/cloud.png",
    "흐림": "assets/cloudy.png",
    "비": "assets/rain.png",
    "소나기":"assets/shower.png"
}

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


# =====================
# 가격 추이
# =====================

if is_mobile:

    left = st.container()
    right = st.container()

else:

    left, right = st.columns([1,2])
history = pd.read_csv("data/garak_history.csv")

special = history[
    history["G_NAME"] == "보통"
].copy()

special["INVEST_DT"] = pd.to_datetime(
    special["INVEST_DT"]
)

special = special.sort_values(
    "INVEST_DT"
)


# 최근 30일===================

recent30 = special.tail(30).copy()

recent30["KG_P"] = (
    recent30["AV_P"] / 20
).round(0)

# 전년 동일일 데이터 생성==========

last_year = special.copy()

last_year["INVEST_DT"] = (
    last_year["INVEST_DT"]
    + pd.DateOffset(years=1)
)

last_year["KG_P_LY"] = (
    last_year["AV_P"] / 20
).round(0)

# 날짜 기준 병합==============

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

# =====================
# 평년 데이터 추가
# =====================

special["KG_P"] = (
    special["AV_P"] / 20
).round(0)

special["MMDD"] = (
    special["INVEST_DT"]
    .dt.strftime("%m-%d")
)

avg_df = (
    special
    .groupby("MMDD")["KG_P"]
    .mean()
    .reset_index()
)

avg_df.columns = [
    "MMDD",
    "KG_P_AVG"
]

chart1["MMDD"] = (
    chart1.index
    .strftime("%m-%d")
)

chart1 = chart1.merge(
    avg_df,
    on="MMDD",
    how="left"
)

chart1 = chart1[
    [
        "MMDD",
        "KG_P",
        "KG_P_LY",
        "KG_P_AVG"
    ]
]

chart1 = chart1.set_index(
    "MMDD"
)

chart1.columns = [
    "올해",
    "전년",
    "평년"
]

# ===========================

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

# 감자시세 제목==============
    st.markdown("""
    <div style="
        background:#FFF4D6;
        padding:8px 12px;
        border-radius:8px;
        font-size:22px;
        font-weight:bold;
        color:#7A4E00;
        margin-bottom:10px;
    ">
        🥔 가락시장 감자 시세
    </div>
    """, unsafe_allow_html=True)

# ========================

    price_cols = st.columns(4)

    for idx, grade in enumerate(["특", "상", "보통", "하"]):

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
                .replace(",", "")
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
                f"{current_price:,}원/kg"
            )

            st.caption(
                f"전년 {last_year_price:,}원/kg"
            )

            if diff_rate > 0:

                st.markdown(
                    f"<span style='color:red'>▲ {diff_rate}%</span>",
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"<span style='color:blue'>▼ {abs(diff_rate)}%</span>",
                    unsafe_allow_html=True
                )

# =============
# 아래 코드는 감자시세 간격
# =============

    st.markdown("""
    <style>

    [data-testid="metric-container"] {
        padding: 0.2rem !important;
    }

    [data-testid="stMetric"] {
        margin-bottom: -15px;
    }

    </style>
    """, unsafe_allow_html=True)

#===============
# 아래는 등락율과 그래프 사이 여백
# ===============

    st.markdown(
        "<hr style='margin-top:5px;margin-bottom:10px;'>",
        unsafe_allow_html=True
    )
#==========================================

# 보통가격 제목=======================
    st.markdown("""
    <div style="
        background:#FFF4D6;
        padding:8px 12px;
        border-radius:8px;
        font-size:20px;
        font-weight:bold;
        color:#7A4E00;
        margin-bottom:5px;
    ">
        📈 최근 30일 보통 가격
    </div>
    """, unsafe_allow_html=True)

# ================================
    st.line_chart(
        chart1,
        height=280
    )
# 평균가격 제목======================
    st.markdown("""
    <div style="
        background:#FFF4D6;
        padding:8px 12px;
        border-radius:8px;
        font-size:20px;
        font-weight:bold;
        color:#7A4E00;
        margin-bottom:5px;
    ">
        📊 월별 평균 가격
    </div>
    """, unsafe_allow_html=True)
#===============================

    st.line_chart(
        chart2,
        height=280
    )

with right:

    mobile = st.query_params.get("mobile") == "1"

    areas = [
        "양구",
        "진부",
        "보성",
        "영광",
        "당진",
        "구미"
    ]

    # ==========================
    # 모바일
    # ==========================
    if mobile:

        st.markdown("""
        <div style="
            background:#FFF4D6;
            padding:10px 14px;
            border-radius:8px;
            font-size:22px;
            font-weight:bold;
            color:#7A4E00;
            margin-bottom:15px;
        ">
            🌞 산지별 10일 예보
        </div>
        """, unsafe_allow_html=True)

        emoji_map = {
            "맑음":"☀️",
            "구름많음":"⛅",
            "흐림":"☁️",
            "비":"🌧️",
            "소나기":"🌦️"
        }

        for area in areas:

            area_df = weather[
                weather["지역"] == area
            ]

            cards = ""

            for _, row in area_df.iterrows():

                weather_text = str(row["오후날씨"])

                icon = "☁️"

                for k,v in emoji_map.items():

                    if k in weather_text:

                        icon = v
                        break

                cards += f"""
                <div style="
                    width:80px;
                    flex:0 0 auto;
                    text-align:center;
                    padding:5px;
                ">
                    <div style="
                        font-weight:bold;
                        font-size:14px;
                    ">
                        {str(row['날짜'])[5:]}
                    </div>

                    <div style="
                        font-size:34px;
                        line-height:1;
                        margin:2px 0;
                    ">
                        {icon}
                    </div>

                    <div style="
                        font-size:11px;
                        color:#666;
                    ">
                        {row['최저기온']}~{row['최고기온']}°
                    </div>

                    <div style="
                        font-size:11px;
                        color:#666;
                    ">
                        💧{row['오후강수확률']}
                    </div>
                """

            html = f"""
            <div style="margin-bottom:10px;">
                <div style="
                    font-size:20px;
                    font-weight:bold;
                    margin-bottom:2px;
                ">
                    📍 {area}
                </div>

                <div style="
                    display:flex;
                    overflow-x:auto;
                    gap:4px;
                    padding-bottom:2px;
                ">
                    {cards}
            </div>
            """

            components.html(
                html,
                height=140,
                scrolling=True
            )

    # ==========================
    # PC
    # ==========================
    else:

        st.markdown("""
        <div style="
            background:#FFF4D6;
            padding:8px 12px;
            border-radius:8px;
            font-size:22px;
            font-weight:bold;
            color:#7A4E00;
            margin-bottom:10px;
        ">
            🌞 산지별 10일 예보
        </div>
        """, unsafe_allow_html=True)

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

                        st.image(
                            icon_path,
                            width=70
                        )

                    st.markdown(
                        f"""
                        <div style="
                            text-align:left;
                            font-size:15px;
                            color:#888;
                            margin-top:-5px;
                        ">
                            {row['최저기온']}~{row['최고기온']}°C
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f"""
                        <div style="
                            text-align:left;
                            font-size:15px;
                            color:#888;
                            margin-top:-4px;
                            margin-bottom:-8px;
                        ">
                            💧 {row['오후강수확률']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown(
                "<hr style='margin-top:2px;margin-bottom:2px;'>",
                unsafe_allow_html=True
            )
