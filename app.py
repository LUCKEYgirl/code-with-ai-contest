import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# 页面配置
# ==============================
st.set_page_config(
    page_title="5G 信号可视化看板",
    page_icon="📶",
    layout="wide"
)

st.title("📶 5G 信号可视化看板")
st.markdown("### Code with AI 海选赛作品")
st.divider()

# ==============================
# 1. 从项目 data 目录读取 CSV（比赛要求）
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("data/signal_samples.csv")
    df = df.dropna(subset=["Latitude", "Longitude", "RSRP_dBm"])
    return df

df = load_data()

# ==============================
# 2. 侧边栏筛选（进阶关卡）
# ==============================
st.sidebar.header("🔍 筛选条件")

# 频段筛选
bands = sorted(df["Band"].unique())
selected_band = st.sidebar.multiselect("选择频段", bands, default=bands)

# RSRP 筛选
rsrp_min = int(df["RSRP_dBm"].min())
rsrp_max = int(df["RSRP_dBm"].max())
rsrp_low, rsrp_high = st.sidebar.slider(
    "RSRP 信号强度 (dBm)",
    min_value=rsrp_min,
    max_value=rsrp_max,
    value=(rsrp_min, rsrp_max)
)

# 筛选后数据
df_filtered = df[
    (df["Band"].isin(selected_band)) &
    (df["RSRP_dBm"] >= rsrp_low) &
    (df["RSRP_dBm"] <= rsrp_high)
].copy()

st.sidebar.metric("当前信号点数", len(df_filtered))

# ==============================
# 3. 信号颜色定义（完全按比赛规则）
# ==============================
def get_color(rsrp):
    if rsrp > -90:
        return "#00FF00"   # 绿：强信号
    elif rsrp < -110:
        return "#FF0000"   # 红：弱信号
    else:
        return "#FFA500"   # 橙：中等

df_filtered["color"] = df_filtered["RSRP_dBm"].apply(get_color)

# ==============================
# 4. 地图（高德底图，秒开，颜色正确）
# ==============================
st.subheader("🌍 5G 信号分布地图")
st.map(
    data=df_filtered,
    latitude="Latitude",
    longitude="Longitude",
    color="color",
    size=15
)

# 颜色说明
st.caption("🟢 强信号(>-90dBm)  🟠 中等(-110~-90dBm)  🔴 弱信号(< -110dBm)")

# ==============================
# 5. 数据统计图表（基础关卡必做）
# ==============================
st.divider()
st.subheader("📊 数据统计")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**各频段基站数量**")
    band_count = df_filtered["Band"].value_counts().reset_index()
    band_count.columns = ["Band", "count"]
    fig1 = px.bar(band_count, x="Band", y="count", color="Band")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("**终端类型分布**")
    terminal_count = df_filtered["TerminalType"].value_counts().reset_index()
    terminal_count.columns = ["TerminalType", "count"]
    fig2 = px.pie(terminal_count, values="count", names="TerminalType")
    st.plotly_chart(fig2, use_container_width=True)

# ==============================
# 6. 数据预览
# ==============================
st.divider()
with st.expander("查看原始数据"):
    st.dataframe(df_filtered, use_container_width=True)