"""
5G 信号可视化看板
用于展示路测数据的信号强度、基站分布和终端类型统计
"""

import streamlit as st
import pandas as pd
import pydeck as pdk

# 页面配置
st.set_page_config(page_title="5G 信号可视化看板", layout="wide")

# 大标题
st.title("📡 5G 信号可视化看板")

# 数据加载（带缓存优化）
@st.cache_data
def load_data():
    """加载 CSV 数据并缓存"""
    return pd.read_csv("data/signal_samples.csv")

df = load_data()

# ==================== 侧边栏筛选器 ====================
st.sidebar.header("筛选条件")

# 频段筛选
bands = df["Band"].unique().tolist()
selected_bands = st.sidebar.multiselect("频段筛选", bands, default=bands)

# 终端类型筛选
terminals = df["TerminalType"].unique().tolist()
selected_terminals = st.sidebar.multiselect("终端类型", terminals, default=terminals)

# RSRP 范围滑动条
rsrp_min, rsrp_max = int(df["RSRP_dBm"].min()), int(df["RSRP_dBm"].max())
rsrp_range = st.sidebar.slider("RSRP 范围 (dBm)", rsrp_min, rsrp_max, (rsrp_min, rsrp_max))

# 下载速率范围滑动条
download_min, download_max = int(df["Download_Mbps"].min()), int(df["Download_Mbps"].max())
download_range = st.sidebar.slider("下载速率范围 (Mbps)", download_min, download_max, (download_min, download_max))

# 联动筛选：根据筛选条件过滤数据
df_filtered = df[
    (df["Band"].isin(selected_bands)) &
    (df["TerminalType"].isin(selected_terminals)) &
    (df["RSRP_dBm"] >= rsrp_range[0]) &
    (df["RSRP_dBm"] <= rsrp_range[1]) &
    (df["Download_Mbps"] >= download_range[0]) &
    (df["Download_Mbps"] <= download_range[1])
]

# 数据概览
st.subheader(f"数据概览：共 {len(df_filtered)} 条记录（原始 {len(df)} 条）")

# ==================== 信号点颜色映射 ====================
def get_color(rsrp):
    """
    根据 RSRP 信号强度返回颜色
    - 绿色: RSRP > -90dBm (信号强)
    - 黄色: -110dBm <= RSRP <= -90dBm (信号中等)
    - 红色: RSRP < -110dBm (信号弱)
    """
    if rsrp > -90:
        return [0, 255, 0]
    elif rsrp < -110:
        return [255, 0, 0]
    else:
        return [255, 165, 0]

# 为过滤后的数据添加颜色列
df_filtered = df_filtered.copy()
df_filtered["color"] = df_filtered["RSRP_dBm"].apply(get_color)

# ==================== 3D 地图渲染 ====================
# 使用 pydeck 渲染 3D 柱状图，信号点根据 RSRP 变色
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=df_filtered["Latitude"].mean(),
        longitude=df_filtered["Longitude"].mean(),
        zoom=12,
        pitch=45,  # 俯仰角 45°
    ),
    layers=[
        pdk.Layer(
            "ColumnLayer",
            data=df_filtered,
            get_position="[Longitude, Latitude]",
            get_elevation="Download_Mbps",  # 高度随下载速率变化
            get_fill_color="color",
            radius=30,
            elevation_scale=1,
            pickable=True,
            extruded=True,  # 3D 柱状图
        )
    ],
    tooltip={"text": "RSRP: {RSRP_dBm} dBm\n下载速率: {Download_Mbps} Mbps\n频段: {Band}"}
))

# ==================== 数据概览图表 ====================
col1, col2 = st.columns(2)

with col1:
    st.subheader("各频段基站数量")
    band_counts = df_filtered["Band"].value_counts()
    st.bar_chart(band_counts)

with col2:
    st.subheader("终端类型占比")
    terminal_counts = df_filtered["TerminalType"].value_counts()
    st.pyplot(terminal_counts.plot.pie(autopct='%1.1f%%', ylabel='').figure)

# 高级数据分析
col3, col4 = st.columns(2)

with col3:
    st.subheader("RSRP 分布直方图")
    st.bar_chart(df_filtered["RSRP_dBm"].value_counts(bins=10).sort_index())

with col4:
    st.subheader("SINR 与 RSRP 相关性")
    scatter_data = df_filtered[["RSRP_dBm", "SINR_dB"]].copy()
    st.scatter_chart(scatter_data, x="RSRP_dBm", y="SINR_dB")