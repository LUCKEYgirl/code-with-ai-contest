"""
5G 信号可视化看板 - "Code with AI" 海选赛
=============================================
功能模块：
  1. 数据加载与概览
  2. 信号热力/散点地图（RSRP 变色）
  3. 数据概览图表（频段基站数量 & 终端类型占比）
  4. 侧边栏联动筛选（频段、RSRP 范围、终端类型）
  5. 3D 地图（pydeck，柱高随下载速率变化）
  6. 工程化注释 & 单元测试
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="5G 信号可视化看板",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 自定义 CSS 样式
# ============================================================
st.markdown("""
<style>
    /* 全局字体与背景 */
    .main {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #e0e0e0;
    }
    /* 标题样式 */
    h1 {
        text-align: center;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
    }
    h2, h3 {
        color: #00d2ff !important;
    }
    /* 侧边栏样式 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
    /* 指标卡片 */
    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(0,210,255,0.3);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .metric-card .value {
        font-size: 2rem;
        font-weight: bold;
        color: #00d2ff;
    }
    .metric-card .label {
        font-size: 0.9rem;
        color: #aaa;
    }
    /* Streamlit 原生组件颜色覆盖 */
    .stDataFrame {
        background-color: rgba(255,255,255,0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 数据加载
# ============================================================
@st.cache_data
def load_data(csv_path: str = "data/signal_samples.csv") -> pd.DataFrame:
    """
    使用 pandas 读取 CSV 数据集。

    Args:
        csv_path: CSV 文件路径，默认为 data/signal_samples.csv

    Returns:
        pd.DataFrame: 加载后的 5G 信号数据
    """
    df = pd.read_csv(csv_path)
    return df


# 加载数据
df = load_data()

# ============================================================
# 页面标题
# ============================================================
st.title("📡 5G 信号可视化看板")
st.markdown("---")

# ============================================================
# 侧边栏 - 联动筛选器（进阶关卡）
# ============================================================
with st.sidebar:
    st.header("🎛️ 数据筛选器")

    # --- 频段筛选（下拉菜单） ---
    all_bands = sorted(df["Band"].unique().tolist())
    selected_bands = st.multiselect(
        "选择频段 (Band)",
        options=all_bands,
        default=all_bands,
        help="选择一个或多个频段进行筛选",
    )

    # --- 终端类型筛选（下拉菜单） ---
    all_terminals = sorted(df["TerminalType"].unique().tolist())
    selected_terminals = st.multiselect(
        "选择终端类型",
        options=all_terminals,
        default=all_terminals,
        help="选择一个或多个终端类型进行筛选",
    )

    # --- RSRP 范围筛选（滑动条） ---
    rsrp_min_val = float(df["RSRP_dBm"].min())
    rsrp_max_val = float(df["RSRP_dBm"].max())
    selected_rsrp_range = st.slider(
        "RSRP 范围 (dBm)",
        min_value=rsrp_min_val,
        max_value=rsrp_max_val,
        value=(rsrp_min_val, rsrp_max_val),
        step=1.0,
        help="拖动滑块筛选信号强度范围",
    )

    # --- SINR 范围筛选 ---
    sinr_min_val = float(df["SINR_dB"].min())
    sinr_max_val = float(df["SINR_dB"].max())
    selected_sinr_range = st.slider(
        "SINR 范围 (dB)",
        min_value=sinr_min_val,
        max_value=sinr_max_val,
        value=(sinr_min_val, sinr_max_val),
        step=0.5,
        help="拖动滑块筛选信噪比范围",
    )

    st.markdown("---")
    st.caption("💡 调整筛选器后，地图和图表将实时更新")

# ============================================================
# 数据过滤
# ============================================================
filtered_df = df[
    (df["Band"].isin(selected_bands))
    & (df["TerminalType"].isin(selected_terminals))
    & (df["RSRP_dBm"] >= selected_rsrp_range[0])
    & (df["RSRP_dBm"] <= selected_rsrp_range[1])
    & (df["SINR_dB"] >= selected_sinr_range[0])
    & (df["SINR_dB"] <= selected_sinr_range[1])
].copy()

# ============================================================
# RSRP 信号强度 -> 颜色映射函数
# ============================================================
def rsrp_to_color(rsrp: float) -> list:
    """
    根据 RSRP 值映射为 RGBA 颜色。
    - 大于 -90 dBm → 绿色 (优秀)
    - -90 ~ -100 dBm → 黄色 (良好)
    - -100 ~ -110 dBm → 橙色 (一般)
    - 小于 -110 dBm → 红色 (较差)

    Args:
        rsrp: RSRP 信号强度值 (dBm)

    Returns:
        list: [R, G, B, A] 颜色值
    """
    if rsrp >= -90:
        return [0, 255, 0, 200]       # 绿色 - 优秀信号
    elif rsrp >= -100:
        return [255, 255, 0, 200]     # 黄色 - 良好信号
    elif rsrp >= -110:
        return [255, 165, 0, 200]     # 橙色 - 一般信号
    else:
        return [255, 0, 0, 200]       # 红色 - 较差信号


# 为过滤后的数据添加颜色列
filtered_df["color"] = filtered_df["RSRP_dBm"].apply(rsrp_to_color)

# ============================================================
# 指标卡片概览
# ============================================================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f'<div class="metric-card"><div class="value">{len(filtered_df)}</div><div class="label">信号采样点</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    avg_rsrp = filtered_df["RSRP_dBm"].mean() if len(filtered_df) > 0 else 0
    st.markdown(
        f'<div class="metric-card"><div class="value">{avg_rsrp:.1f}</div><div class="label">平均 RSRP (dBm)</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    avg_sinr = filtered_df["SINR_dB"].mean() if len(filtered_df) > 0 else 0
    st.markdown(
        f'<div class="metric-card"><div class="value">{avg_sinr:.1f}</div><div class="label">平均 SINR (dB)</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    avg_dl = filtered_df["Download_Mbps"].mean() if len(filtered_df) > 0 else 0
    st.markdown(
        f'<div class="metric-card"><div class="value">{avg_dl:.1f}</div><div class="label">平均下载速率 (Mbps)</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ============================================================
# Tab 切换：2D 地图 / 3D 地图
# ============================================================
tab_2d, tab_3d = st.tabs(["🗺️ 2D 信号地图", "🌐 3D 极客地图"])

# ============================================================
# 2D 信号散点地图（基础关卡）
# ============================================================
with tab_2d:
    st.subheader("信号强度散点地图")
    st.caption("地图上的点根据 RSRP 信号强度变色：🟢 优秀(≥-90) 🟡 良好(-100~-90) 🟠 一般(-110~-100) 🔴 较差(<-110)")

    if len(filtered_df) > 0:
        # 使用 pydeck ScatterplotLayer 渲染交互式散点地图
        # 计算地图中心点
        center_lat = filtered_df["Latitude"].mean()
        center_lon = filtered_df["Longitude"].mean()

        # 构建 pydeck 视图状态
        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=0,
            bearing=0,
        )

        # 散点图层
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position="[Longitude, Latitude]",
            get_color="color",
            get_radius=80,
            pickable=True,
            opacity=0.8,
            auto_highlight=True,
        )

        # 工具提示
        tooltip = {
            "html": """
            <div style="font-family: Arial; padding: 8px;">
                <b>小区ID:</b> {CellID}<br/>
                <b>频段:</b> {Band}<br/>
                <b>RSRP:</b> {RSRP_dBm} dBm<br/>
                <b>SINR:</b> {SINR_dB} dB<br/>
                <b>终端类型:</b> {TerminalType}<br/>
                <b>下载速率:</b> {Download_Mbps} Mbps
            </div>
            """,
            "style": {
                "backgroundColor": "rgba(0,0,0,0.8)",
                "color": "white",
                "borderRadius": "8px",
            },
        }

        # 渲染地图
        st.pydeck_chart(
            pdk.Deck(
                layers=[scatter_layer],
                initial_view_state=view_state,
                map_style="mapbox://styles/mapbox/dark-v11",
                tooltip=tooltip,
            )
        )
    else:
        st.warning("⚠️ 当前筛选条件下没有数据，请调整筛选器。")

# ============================================================
# 3D 极客地图（进阶关卡 - 3D 柱状图）
# ============================================================
with tab_3d:
    st.subheader("3D 信号柱状地图")
    st.caption("信号点以 3D 柱状图形式展示，柱高随下载速率 (Download_Mbps) 变化")

    if len(filtered_df) > 0:
        center_lat = filtered_df["Latitude"].mean()
        center_lon = filtered_df["Longitude"].mean()

        # 3D 视图状态（带俯仰角）
        view_state_3d = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=45,
            bearing=0,
        )

        # 3D 柱状图层（ColumnLayer）
        column_layer = pdk.Layer(
            "ColumnLayer",
            data=filtered_df,
            get_position="[Longitude, Latitude]",
            get_elevation="Download_Mbps",
            get_color="color",
            elevation_scale=0.05,  # 缩放因子，使柱高适中
            radius=50,
            pickable=True,
            opacity=0.85,
            auto_highlight=True,
        )

        tooltip_3d = {
            "html": """
            <div style="font-family: Arial; padding: 8px;">
                <b>小区ID:</b> {CellID}<br/>
                <b>频段:</b> {Band}<br/>
                <b>RSRP:</b> {RSRP_dBm} dBm<br/>
                <b>下载速率:</b> {Download_Mbps} Mbps<br/>
                <b>终端类型:</b> {TerminalType}
            </div>
            """,
            "style": {
                "backgroundColor": "rgba(0,0,0,0.8)",
                "color": "white",
                "borderRadius": "8px",
            },
        }

        st.pydeck_chart(
            pdk.Deck(
                layers=[column_layer],
                initial_view_state=view_state_3d,
                map_style="mapbox://styles/mapbox/dark-v11",
                tooltip=tooltip_3d,
            )
        )
    else:
        st.warning("⚠️ 当前筛选条件下没有数据，请调整筛选器。")

st.markdown("---")

# ============================================================
# 数据概览图表（基础关卡）
# ============================================================
st.subheader("📊 数据概览图表")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### 各频段基站数量")
    # 统计各频段的基站（CellID）数量
    band_counts = (
        filtered_df.groupby("Band")["CellID"]
        .nunique()
        .reset_index()
        .rename(columns={"CellID": "基站数量"})
    )
    # 使用 Streamlit 原生柱状图
    st.bar_chart(band_counts, x="Band", y="基站数量", color="#00d2ff")

with chart_col2:
    st.markdown("#### 终端类型占比")
    # 统计不同终端类型的采样点数量
    terminal_counts = filtered_df["TerminalType"].value_counts().reset_index()
    terminal_counts.columns = ["终端类型", "数量"]
    # 使用 Streamlit 原生柱状图展示占比
    st.bar_chart(terminal_counts, x="终端类型", y="数量", color="#3a7bd5")

st.markdown("---")

# ============================================================
# RSRP 信号分布直方图
# ============================================================
st.subheader("📈 RSRP 信号强度分布")
st.caption("展示当前筛选数据中 RSRP 信号强度的分布情况")

hist_col1, hist_col2 = st.columns(2)

with hist_col1:
    st.markdown("#### RSRP 分布直方图")
    if len(filtered_df) > 0:
        st.bar_chart(
            filtered_df["RSRP_dBm"]
            .value_counts(bins=10)
            .sort_index(),
            color="#00d2ff",
        )
    else:
        st.warning("无数据")

with hist_col2:
    st.markdown("#### SINR 分布直方图")
    if len(filtered_df) > 0:
        st.bar_chart(
            filtered_df["SINR_dB"]
            .value_counts(bins=10)
            .sort_index(),
            color="#3a7bd5",
        )
    else:
        st.warning("无数据")

st.markdown("---")

# ============================================================
# 数据表格预览
# ============================================================
st.subheader("📋 数据预览")
st.caption(f"当前筛选结果共 {len(filtered_df)} 条记录（原始数据 {len(df)} 条）")
st.dataframe(
    filtered_df.drop(columns=["color"]),
    use_container_width=True,
    height=300,
    hide_index=True,
)

# ============================================================
# 页脚
# ============================================================
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#666;">📡 5G 信号可视化看板 | "Code with AI" 海选赛作品 | Powered by Streamlit & PyDeck</p>',
    unsafe_allow_html=True,
)
