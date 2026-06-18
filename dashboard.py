import streamlit as st
import pandas as pd
import subprocess
import plotly.graph_objects as go
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval
import os
from datetime import datetime


st.set_page_config(
    page_title="Potato Times",
    layout="wide"
)

# ==========================
# 모바일 자동 감지
# ==========================

try:

    screen_width = streamlit_js_eval(
        js_expressions="window.innerWidth",
        key="WIDTH"
    )

    mobile = (
        screen_width is not None
        and screen_width < 768
    )

except:

    mobile = False

# =======================================

st.markdown("""
<style>

.block-container {
    padding-top: 3rem;
    padding-bottom: 0rem;
    padding-left: 1rem;
    padding-right: 1rem;
    max-width: 110%;
}

h1,h2,h3 {
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

# ==========================
# 헤더
# ==========================

if mobile:

    header_left, header_right = st.columns([4, 1])

    title_size = "34px"
    status_size = "10px"
    status_margin = "4px"

else:

    header_left, header_right = st.columns([8, 1])

    title_size = "58px"
    status_size = "12px"
    status_margin = "18px"

with header_left:

    st.markdown(
        f"""
        <div style="
            font-family:'Palatino Linotype', serif;
            font-size:{title_size};
            font-weight:bold;
            color:#203864;
            line-height:1.0;
            margin-top:0px;
            margin-bottom:0px;
            white-space:nowrap;
        ">
            🥔 Potato Times
        </div>
        """,
        unsafe_allow_html=True
    )

with header_right:

    st.markdown(
        f"""
        <div style="
            background:#DFF5E1;
            color:#155724;
            padding:4px;
            border-radius:6px;
            text-align:center;
            font-size:{status_size};
            font-weight:bold;
            margin-top:{status_margin};
        ">
            정상<br>
            {datetime.today().strftime("%Y-%m-%d")}
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("""
<hr style="
    margin-top:5px;
    margin-bottom:5px;
    border:none;
    border-top:1px solid #D9D9D9;
">
""", unsafe_allow_html=True)

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

        title_size = "14px" if mobile else "15px"
        body_size = "13px" if mobile else "14px"

        st.markdown(
            f"""
<div style="
    background:#EDF4FF;
    border-left:4px solid #4A90E2;
    padding:8px 12px;
    border-radius:6px;
    margin-top:0px;
    margin-bottom:0px;
">

<b style="
    color:#1f4f9c;
    font-size:{title_size};
">
📢 KAMIS 시장동향 | {title}
</b>

<br>

<span style="
    color:#444;
    font-size:{body_size};
    line-height:1.3;
">
{summary}
</span>

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
    "소나기": "assets/shower.png"
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

# =====================
# PC / 모바일 레이아웃
# =====================

if mobile:

    left = st.container()
    right = st.container()

else:

    left, right = st.columns([1, 2])

# =============================

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

# 최근 30일 ===================

recent30 = special.tail(30).copy()

recent30["KG_P"] = (
    recent30["AV_P"] / 20
).round(0)

# 전년 동일일 데이터 생성 ==========

last_year = special.copy()

last_year["INVEST_DT"] = (
    last_year["INVEST_DT"]
    + pd.DateOffset(years=1)
)

last_year["KG_P_LY"] = (
    last_year["AV_P"] / 20
).round(0)

# 날짜 기준 병합 ==============

chart1 = pd.merge(
    recent30[["INVEST_DT", "KG_P"]],
    last_year[["INVEST_DT", "KG_P_LY"]],
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

    # =====================
    # 가락시장 감자 시세
    # =====================

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

    # =====================
    # 시세 표시
    # =====================

    if mobile:

        row_html = ""

        for grade in ["특", "상", "보통", "하"]:

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

            row_html += f"""
            <td style="text-align:center;">
                <div style="font-weight:bold;">
                    {grade}
                </div>
                <div style="
                    font-size:22px;
                    font-weight:bold;
                ">
                    {current_price:,}
                </div>
                <div style="
                    font-size:11px;
                    color:#0A36FF;
                ">
                    ▼ {abs(diff_rate)}%
                </div>
            """

        st.markdown(
            f"""
            <table style="
                width:100%;
                table-layout:fixed;
            ">
                <tr>
                    {row_html}
            </table>
            """,
            unsafe_allow_html=True
        )

    else:

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
                    label=grade,
                    value=f"{current_price:,}원/kg"
                )

                st.caption(
                    f"전년 {last_year_price:,}원/kg"
                )

                if diff_rate > 0:

                    st.markdown(
                        f"<span style='color:red;font-size:12px;'>▲ {diff_rate}%</span>",
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        f"<span style='color:blue;font-size:12px;'>▼ {abs(diff_rate)}%</span>",
                        unsafe_allow_html=True
                    )

    # =====================
    # 시세 영역 스타일
    # =====================

    st.markdown("""
    <style>

    [data-testid="metric-container"] {
        padding: 0.15rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.3rem !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # =====================
    # 그래프와의 간격
    # =====================

    st.markdown(
        "<hr style='margin-top:5px;margin-bottom:2px;'>",
        unsafe_allow_html=True
    )

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

    data_max = chart1.max().max()
    data_min = chart1.min().min()

    ymax = int(data_max + 100)
    ymin = int(data_min - 100)

    x_labels = [str(x) for x in chart1.index]

    # 마지막 날짜 기준 2일 간격
    tick_idx = list(
        range(
            len(x_labels) - 1,
            -1,
            -2
        )
    )

    tick_idx.reverse()

    tickvals = [
        x_labels[i]
        for i in tick_idx
    ]

    fig1 = go.Figure()

    fig1.add_trace(
        go.Scatter(
            x=x_labels,
            y=chart1["올해"],
            mode="lines",
            name="올해",
            line=dict(
                color="#1565C0",
                width=3
            )
        )
    )

    fig1.add_trace(
        go.Scatter(
            x=x_labels,
            y=chart1["전년"],
            mode="lines",
            name="전년",
            line=dict(
                color="#64B5F6",
                width=2
            )
        )
    )

    fig1.add_trace(
        go.Scatter(
            x=x_labels,
            y=chart1["평년"],
            mode="lines",
            name="평년",
            line=dict(
                color="gray",
                width=2
            )
        )
    )

    max_idx = chart1["올해"].idxmax()
    min_idx = chart1["올해"].idxmin()
    last_idx = chart1.index[-1]

    # 최고점
    fig1.add_annotation(
        x=str(max_idx),
        y=chart1["올해"].max(),
        text=f"최고 {int(chart1['올해'].max()):,}원",
        showarrow=False,
        yshift=18,
        font=dict(
            size=10 if mobile else 12,
            color="#1565C0"
        )
    )

    # 최저점
    fig1.add_annotation(
        x=str(min_idx),
        y=chart1["올해"].min(),
        text=f"최저 {int(chart1['올해'].min()):,}원",
        showarrow=False,
        yshift=18,
        font=dict(
            size=10 if mobile else 12,
            color="#1565C0"
        )
    )

    # 최신값
    fig1.add_annotation(
        x=str(last_idx),
        y=chart1["올해"].iloc[-1],
        text=f"최신 {int(chart1['올해'].iloc[-1]):,}원",
        showarrow=False,
        xshift=-45,
        yshift=18,
        font=dict(
            size=10 if mobile else 12,
            color="#1565C0"
        )
    )

    fig1.update_layout(
        height=220 if mobile else 280,

        margin=dict(
            l=10,
            r=30,
            t=30,
            b=10
        ),

        hovermode="x unified",
        dragmode=False,

        xaxis=dict(
            type="category",
            tickmode="array",
            tickvals=tickvals,
            ticktext=tickvals
        ),

        yaxis=dict(
            range=[ymin, ymax]
        ),

        legend=dict(
            orientation="h",
            y=1.15,
            x=0,
            bgcolor="rgba(0,0,0,0)"
        )
    )

    st.plotly_chart(
        fig1,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "displayModeBar": False,
            "doubleClick": "reset"
        }
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

    fig2 = go.Figure()

    latest_month = monthly.iloc[-1]["월"][-2:]

    label_df = monthly[
        monthly["월"].str.endswith(
            latest_month
        )
    ].tail(6)

    ymax2 = chart2["KG_P"].max()

    fig2.add_trace(
        go.Scatter(
            x=chart2.index.astype(str),
            y=chart2["KG_P"],
            mode="lines",
            name="가격",
            line=dict(
                width=3
            )
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=label_df["월"],
            y=label_df["KG_P"],
            mode="markers",
            marker=dict(
                size=7
            ),
            showlegend=False
        )
    )

    for _, row in label_df.iterrows():

        fig2.add_vline(
            x=row["월"],
            line_width=1,
            line_dash="dot",
            line_color="rgba(120,120,120,0.35)"
        )

        fig2.add_annotation(
            x=row["월"],
            y=ymax2 + 250,
            text=(
                f"{row['월']}<br>"
                f"{int(row['KG_P']):,}원"
            ),
            showarrow=False,
            font=dict(
                size=9,
                color="gray"
            )
        )

    fig2.update_layout(
        height=220 if mobile else 280,
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),
        hovermode="x unified",
        dragmode=False,
        showlegend=False,
        yaxis=dict(
            range=[
                0,
                ymax2 + 500
            ]
        )
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "displayModeBar": False,
            "doubleClick": "reset"
        }
    )

# =======================================

with right:

    areas = [
        "양구",
        "진부",
        "보성",
        "영광",
        "당진",
        "구미"
    ]

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

    # ===================================
    # 모바일
    # ===================================

    if mobile:

        sample = weather[
            weather["지역"] == "양구"
        ]

        BASE_ICON = (
            "https://raw.githubusercontent.com/"
            "wngml7055/potato-times/main/assets"
        )

        icon_url = {
            "맑음": f"{BASE_ICON}/sunny.png",
            "구름": f"{BASE_ICON}/cloud.png",
            "흐림": f"{BASE_ICON}/cloudy.png",
            "비": f"{BASE_ICON}/rain.png",
            "소나기": f"{BASE_ICON}/shower.png"
        }

        html = """
        <div style="
            overflow-x:auto;
            width:100%;
        ">
        <table style="
            border-collapse:collapse;
            white-space:nowrap;
            text-align:center;
            font-size:13px;
            width:max-content;
        ">
        """

        html += """
        <tr>
            <th style="
                position:sticky;
                left:0;
                background:white;
                z-index:999;
                min-width:50px;
                padding:6px;
                border-bottom:2px solid #DDD;
            ">
                산지
            </th>
        """

        for _, row in sample.iterrows():

            html += f"""
            <th style="
                min-width:85px;
                padding:6px;
                border-bottom:2px solid #DDD;
            ">
                {str(row['날짜'])[5:]}
            </th>
            """

        html += "</tr>"

        for area in areas:

            area_df = weather[
                weather["지역"] == area
            ]

            html += f"""
            <tr>
                <td style="
                    position:sticky;
                    left:0;
                    background:white;
                    font-weight:bold;
                    padding:4px;
                    border-bottom:1px solid #EEE;
                ">
                    {area}
                </td>
            """

            for _, row in area_df.iterrows():

                weather_text = str(
                    row["오후날씨"]
                )

                icon = icon_url["흐림"]

                for key in icon_url:

                    if key in weather_text:

                        icon = icon_url[key]
                        break

                html += f"""
                <td style="
                    min-width:85px;
                    padding:4px;
                    border-bottom:1px solid #EEE;
                ">
                    <img
                        src="{icon}"
                        width="45"
                    >

                    <div style="
                        font-size:10px;
                        color:#666;
                    ">
                        {row['최저기온']}~{row['최고기온']}℃
                    </div>

                    <div style="
                        font-size:10px;
                        color:#666;
                    ">
                        💧 {row['오후강수확률']}
                    </div>
                </td>
                """

            html += "</tr>"

        html += """
        </table>
        </div>
        """

        components.html(
            html,
            height=620,
            scrolling=True
        )

    # ===================================
    # PC
    # ===================================

    else:

        sample = weather[
            weather["지역"] == "양구"
        ]

        header = st.columns(
            len(sample) + 1
        )

        header[0].markdown("**산지**")

        for i, (_, row) in enumerate(
            sample.iterrows()
        ):

            header[i + 1].markdown(
                f"**{str(row['날짜'])[5:]}**"
            )

        for area in areas:

            area_df = weather[
                weather["지역"] == area
            ]

            cols = st.columns(
                len(area_df) + 1,
                gap="small"
            )

            cols[0].markdown(
                f"**{area}**"
            )

            for i, (_, row) in enumerate(
                area_df.iterrows()
            ):

                weather_text = str(
                    row["오후날씨"]
                )

                icon_path = None

                for key in weather_icon:

                    if key in weather_text:

                        icon_path = weather_icon[key]
                        break

                with cols[i + 1]:

                    if icon_path:

                        st.image(
                            icon_path,
                            width=70
                        )

                    st.markdown(
                        f"""
                        <div style="
                            text-align:center;
                            font-size:12px;
                            color:#666;
                            margin-top:-8px;
                        ">
                            {row['최저기온']}~{row['최고기온']}℃
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f"""
                        <div style="
                            text-align:center;
                            font-size:12px;
                            color:#666;
                            margin-top:-4px;
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
