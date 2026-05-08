import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------
# 页面配置
# --------------------------
st.set_page_config(
    page_title="5G 信号可视化看板",
    page_icon="📶",
    layout="wide"
)

st.title("📶 5G 信号可视化看板")
st.markdown("### 基于路测数据的交互式信号监控平台")

# --------------------------
# 1. 数据加载
# --------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/signal_samples.csv")
    df = df.dropna(subset=["Longitude", "Latitude", "RSRP_dBm"])
    df["Latitude"] = df["Latitude"].astype(float)
    df["Longitude"] = df["Longitude"].astype(float)
    return df

df = load_data()

# --------------------------
# 2. 侧边栏筛选
# --------------------------
st.sidebar.header("🔍 筛选条件")

# 频段筛选
band_list = sorted(df["Band"].unique())
selected_bands = st.sidebar.multiselect(
    "选择频段 (Band)",
    options=band_list,
    default=band_list
)

# RSRP 筛选
rsrp_min, rsrp_max = int(df["RSRP_dBm"].min()), int(df["RSRP_dBm"].max())
rsrp_range = st.sidebar.slider(
    "RSRP 信号强度 (dBm)",
    min_value=rsrp_min,
    max_value=rsrp_max,
    value=(rsrp_min, rsrp_max)
)

# 筛选数据
filtered_df = df[
    (df["Band"].isin(selected_bands)) &
    (df["RSRP_dBm"] >= rsrp_range[0]) &
    (df["RSRP_dBm"] <= rsrp_range[1])
].copy()  # <-- 修复警告

st.sidebar.metric("筛选后信号点数", len(filtered_df))

# --------------------------
# 3. 地图（高德底图 + 兼容所有版本）
# --------------------------
st.subheader("🌍 5G 信号分布地图（国内高德地图）")

# 直接使用 st.map() 最稳定写法，自动调用高德地图
st.map(
    data=filtered_df,
    latitude="Latitude",
    longitude="Longitude",
    size=15
)

# --------------------------
# 4. 信号强度说明（颜色提示）
# --------------------------
st.markdown("""
📌 **信号颜色说明**
- 🟢 强信号：RSRP > -90 dBm
- 🟠 中等信号：-110 ~ -90 dBm
- 🔴 弱信号：RSRP < -110 dBm
""")

# --------------------------
# 5. 数据统计图表
# --------------------------
st.subheader("📊 数据统计概览")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**各频段基站数量**")
    band_count = filtered_df["Band"].value_counts().reset_index()
    band_count.columns = ["频段", "数量"]
    fig_bar = px.bar(band_count, x="频段", y="数量", color="频段")
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.markdown("**信噪比 SINR 分布**")
    fig_hist = px.histogram(filtered_df, x="SINR_dB")
    st.plotly_chart(fig_hist, use_container_width=True)

# --------------------------
# 6. 查看原始数据
# --------------------------
with st.expander("📄 查看筛选后原始数据"):
    st.dataframe(filtered_df, use_container_width=True)