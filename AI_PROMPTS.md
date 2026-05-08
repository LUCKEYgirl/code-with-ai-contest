# Agent 交互日志

**团队名称：** CodeAgent Team
**成员名单：** Agent1, Agent2, Agent3
**使用的 AI Coding Agent 工具：** Claude Code / OpenCode

---

## 🤖 交互记录

### 第一轮对话（基础功能）

**用户输入：**
> 请使用 Streamlit 写一个看板，帮我读取当前目录下的 data/signal_samples.csv，在网页上加个大标题，然后用 st.map() 把数据里的纬度(Latitude)和经度(Longitude)画在地图上。

**AI 生成代码：**
```python
import streamlit as st
import pandas as pd

st.set_page_config(page_title="5G信号可视化看板", layout="wide")

st.title("📡 5G 信号可视化看板")

df = pd.read_csv("data/signal_samples.csv")

df_map = df[["Latitude", "Longitude"]].copy()
st.map(df_map)
```

---

### 第二轮对话（阅读题目）

**用户输入：**
> 阅读题目D:\code\codewithai\code-with-ai-contest-main\README.md

**AI 理解需求：** 
- 基础关卡：数据加载、信号地图按RSRP变色、频段统计图
- 进阶关卡：侧边栏筛选、3D地图、单元测试

---

### 第三轮对话（完善代码）

**用户输入：**
> 需要你继续完善代码

**AI 生成代码：**
- 添加侧边栏筛选器（频段多选、RSRP滑动条）
- 使用 pydeck 实现 3D 地图
- 信号点根据 RSRP 变色逻辑
- 添加频段统计和终端类型占比图表
- 添加数据缓存装饰器 `@st.cache_data`

---

### 第四轮对话（检查交付物）

**用户输入：**
> 4 项"硬核交付物"都有吗

**AI 回复：** 
- 缺少 requirements.txt
- 缺少 README.md
- 缺少运行截图
- 缺少 AI_PROMPTS.md

---

### 第五轮对话（生成文件）

**用户输入：**
> 需要

**AI 生成文件：**
- requirements.txt：streamlit, pandas, pydeck
- README.md：项目说明文档
- AI_PROMPTS.md：本文档
- test_app.py：单元测试文件

---

### 第六轮对话（完善功能）

**用户输入：**
> 是否完成进阶关卡

**AI 回复：** 
- 侧边栏联动筛选：✅
- 3D地图：✅
- 单元测试：✅
- 运行 pytest 验证：16个测试全部通过

---

### 第七轮对话（添加注释）

**用户输入：**
> 为核心代码生成规范注释

**AI 添加注释：**
- 模块文档字符串
- 函数功能说明
- 代码区块注释

---

## 代码生成要点总结

### 1. 基础功能
| 功能 | 代码实现 |
|-----|---------|
| CSV数据加载 | `pd.read_csv()` + `@st.cache_data` |
| 散点地图 | `st.map()` |
| 统计图表 | `st.bar_chart()` |

### 2. 进阶功能
| 功能 | 代码实现 |
|-----|---------|
| 侧边栏筛选 | `st.sidebar.multiselect()` + `st.sidebar.slider()` |
| 3D地图 | `pydeck.ColumnLayer` + `extruded=True` |
| RSRP变色 | `get_color()` 函数返回RGB颜色 |
| 联动筛选 | DataFrame 多条件过滤 |

### 3. 工程化
| 项目 | 内容 |
|-----|-----|
| 依赖管理 | requirements.txt |
| 项目文档 | README.md |
| 单元测试 | test_app.py (16个测试用例) |
| 代码注释 | 规范docstring和区块注释 |

---

## 核心算法说明

### RSRP 颜色映射逻辑
```python
def get_color(rsrp):
    if rsrp > -90:      # 信号强 -> 绿色
        return [0, 255, 0]
    elif rsrp < -110:  # 信号弱 -> 红色
        return [255, 0, 0]
    else:              # 信号中等 -> 黄色
        return [255, 165, 0]
```

### 3D 柱状图配置
- 位置：`[Longitude, Latitude]`
- 高度：`get_elevation="Download_Mbps"`
- 颜色：`get_fill_color="color"` (根据RSRP)
- 俯仰角：`pitch=45` (45度角查看)

---

## 验收测试结果

```
============================= test session starts =============================
test_app.py::test_load_data PASSED                                       [  6%]
test_app.py::test_rsrp_color_logic PASSED                                [ 12%]
test_app.py::test_filter_by_band PASSED                                  [ 18%]
test_app.py::test_filter_by_rsrp PASSED                                  [ 25%]
test_app.py::test_band_counts PASSED                                     [ 31%]
test_app.py::test_terminal_type_counts PASSED                            [ 37%]
test_app.py::test_filter_by_terminal PASSED                              [ 43%]
test_app.py::test_filter_by_download PASSED                              [ 50%]
test_app.py::test_combined_filter PASSED                                 [ 56%]
test_app.py::test_data_statistics PASSED                                 [ 62%]
test_app.py::test_unique_bands PASSED                                    [ 68%]
test_app.py::test_unique_terminals PASSED                                [ 75%]
test_app.py::test_latitude_range PASSED                                  [ 81%]
test_app.py::test_longitude_range PASSED                                 [ 87%]
test_app.py::test_sinr_exists PASSED                                     [ 93%]
test_app.py::test_cellid_exists PASSED                                   [100%]

============================= 16 passed in 0.81s ==============================
```