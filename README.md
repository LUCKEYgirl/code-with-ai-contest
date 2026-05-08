5G 信号可视化看板
项目简介
本项目是一个基于 Streamlit 的 5G 信号数据可视化看板，用于展示路测数据的信号强度、基站分布和终端类型统计。

功能特性
基础功能
数据加载：读取 CSV 格式的 5G 路测数据
交互式地图：显示信号点分布，根据 RSRP 信号强度自动变色
绿色：信号强（RSRP > -90dBm）
橙色：信号中等（-110dBm ≤ RSRP ≤ -90dBm）
红色：信号弱（RSRP < -110dBm）
数据统计：频段基站数量柱状图、终端类型占比图
进阶功能
侧边栏联动筛选：支持按频段、RSRP 范围筛选
3D 可视化地图：信号点以 3D 柱状图形式展示，高度随下载速率变化
运行方法
1. 安装依赖
pip install -r requirements.txt
2. 启动应用
streamlit run app.py
3. 访问看板
浏览器打开 http://localhost:8501

数据说明
数据文件：data/signal_samples.csv

字段说明：

Latitude：纬度
Longitude：经度
CellID：小区 ID
Band：频段（n28, n41, n78）
RSRP_dBm：信号强度
SINR_dB：信噪比
TerminalType：终端类型（Smartphone, CPE, IoT）
Download_Mbps：下载速率
技术栈
Python 3.8+
Streamlit
Pandas
Pydeck