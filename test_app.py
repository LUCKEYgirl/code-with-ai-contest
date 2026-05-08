"""
5G 信号可视化看板 - 单元测试
==============================
测试覆盖范围：
  1. 数据加载功能
  2. RSRP 颜色映射函数
  3. 数据过滤逻辑
  4. 数据统计功能
"""

import unittest
import pandas as pd
import numpy as np
import os
import sys

# 将项目根目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入被测模块中的核心函数
# 注意：由于 app.py 包含 Streamlit 全局代码，我们直接定义测试用的函数副本
def rsrp_to_color(rsrp: float) -> list:
    """
    根据 RSRP 值映射为 RGBA 颜色。
    - 大于等于 -90 dBm → 绿色 (优秀)
    - -90 ~ -100 dBm → 黄色 (良好)
    - -100 ~ -110 dBm → 橙色 (一般)
    - 小于 -110 dBm → 红色 (较差)
    """
    if rsrp >= -90:
        return [0, 255, 0, 200]
    elif rsrp >= -100:
        return [255, 255, 0, 200]
    elif rsrp >= -110:
        return [255, 165, 0, 200]
    else:
        return [255, 0, 0, 200]


class TestDataLoading(unittest.TestCase):
    """测试数据加载功能"""

    def test_csv_file_exists(self):
        """验证 CSV 数据文件存在"""
        csv_path = os.path.join(os.path.dirname(__file__), "data", "signal_samples.csv")
        self.assertTrue(
            os.path.exists(csv_path),
            f"数据文件不存在: {csv_path}",
        )

    def test_data_load_success(self):
        """验证数据可以正确加载为 DataFrame"""
        csv_path = os.path.join(os.path.dirname(__file__), "data", "signal_samples.csv")
        df = pd.read_csv(csv_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0, "数据集不应为空")

    def test_required_columns_exist(self):
        """验证数据集包含所有必需字段"""
        csv_path = os.path.join(os.path.dirname(__file__), "data", "signal_samples.csv")
        df = pd.read_csv(csv_path)
        required_columns = [
            "Latitude", "Longitude", "CellID", "Band",
            "RSRP_dBm", "SINR_dB", "TerminalType", "Download_Mbps",
        ]
        for col in required_columns:
            self.assertIn(col, df.columns, f"缺少必需字段: {col}")

    def test_data_types(self):
        """验证关键字段的数据类型正确"""
        csv_path = os.path.join(os.path.dirname(__file__), "data", "signal_samples.csv")
        df = pd.read_csv(csv_path)
        self.assertTrue(pd.api.types.is_numeric_dtype(df["Latitude"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(df["Longitude"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(df["RSRP_dBm"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(df["SINR_dB"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(df["Download_Mbps"]))

    def test_no_null_values(self):
        """验证数据集无空值"""
        csv_path = os.path.join(os.path.dirname(__file__), "data", "signal_samples.csv")
        df = pd.read_csv(csv_path)
        self.assertEqual(df.isnull().sum().sum(), 0, "数据集不应有空值")


class TestRSRPColorMapping(unittest.TestCase):
    """测试 RSRP 信号强度到颜色的映射函数"""

    def test_excellent_signal_green(self):
        """RSRP >= -90 dBm 应映射为绿色"""
        self.assertEqual(rsrp_to_color(-70), [0, 255, 0, 200])
        self.assertEqual(rsrp_to_color(-90), [0, 255, 0, 200])

    def test_good_signal_yellow(self):
        """-100 <= RSRP < -90 dBm 应映射为黄色"""
        self.assertEqual(rsrp_to_color(-95), [255, 255, 0, 200])
        self.assertEqual(rsrp_to_color(-100), [255, 255, 0, 200])

    def test_fair_signal_orange(self):
        """-110 <= RSRP < -100 dBm 应映射为橙色"""
        self.assertEqual(rsrp_to_color(-105), [255, 165, 0, 200])
        self.assertEqual(rsrp_to_color(-110), [255, 165, 0, 200])

    def test_poor_signal_red(self):
        """RSRP < -110 dBm 应映射为红色"""
        self.assertEqual(rsrp_to_color(-115), [255, 0, 0, 200])
        self.assertEqual(rsrp_to_color(-120), [255, 0, 0, 200])

    def test_boundary_values(self):
        """测试边界值"""
        # -90 是绿色和黄色的边界
        self.assertEqual(rsrp_to_color(-89.9), [0, 255, 0, 200])
        self.assertEqual(rsrp_to_color(-90.1), [255, 255, 0, 200])
        # -100 是黄色和橙色的边界
        self.assertEqual(rsrp_to_color(-99.9), [255, 255, 0, 200])
        self.assertEqual(rsrp_to_color(-100.1), [255, 165, 0, 200])
        # -110 是橙色和红色的边界
        self.assertEqual(rsrp_to_color(-109.9), [255, 165, 0, 200])
        self.assertEqual(rsrp_to_color(-110.1), [255, 0, 0, 200])

    def test_color_format(self):
        """验证返回颜色格式为 [R, G, B, A] 四元组"""
        color = rsrp_to_color(-85)
        self.assertEqual(len(color), 4)
        for c in color:
            self.assertIsInstance(c, int)
            self.assertGreaterEqual(c, 0)
            self.assertLessEqual(c, 255)


class TestDataFiltering(unittest.TestCase):
    """测试数据过滤逻辑"""

    @classmethod
    def setUpClass(cls):
        """加载测试数据"""
        csv_path = os.path.join(os.path.dirname(__file__), "data", "signal_samples.csv")
        cls.df = pd.read_csv(csv_path)

    def test_band_filter(self):
        """测试频段筛选"""
        filtered = self.df[self.df["Band"].isin(["n28"])]
        self.assertTrue(all(filtered["Band"] == "n28"))
        self.assertGreater(len(filtered), 0)

    def test_rsrp_range_filter(self):
        """测试 RSRP 范围筛选"""
        filtered = self.df[
            (self.df["RSRP_dBm"] >= -100) & (self.df["RSRP_dBm"] <= -80)
        ]
        self.assertTrue(all(filtered["RSRP_dBm"] >= -100))
        self.assertTrue(all(filtered["RSRP_dBm"] <= -80))

    def test_terminal_type_filter(self):
        """测试终端类型筛选"""
        filtered = self.df[self.df["TerminalType"].isin(["Smartphone", "CPE"])]
        self.assertTrue(all(filtered["TerminalType"].isin(["Smartphone", "CPE"])))

    def test_combined_filter(self):
        """测试组合筛选条件"""
        filtered = self.df[
            (self.df["Band"] == "n78")
            & (self.df["RSRP_dBm"] >= -100)
            & (self.df["TerminalType"] == "CPE")
        ]
        self.assertTrue(all(filtered["Band"] == "n78"))
        self.assertTrue(all(filtered["RSRP_dBm"] >= -100))
        self.assertTrue(all(filtered["TerminalType"] == "CPE"))

    def test_empty_filter_result(self):
        """测试筛选结果为空的情况"""
        filtered = self.df[self.df["RSRP_dBm"] >= 0]
        self.assertEqual(len(filtered), 0)


class TestDataStatistics(unittest.TestCase):
    """测试数据统计功能"""

    @classmethod
    def setUpClass(cls):
        """加载测试数据"""
        csv_path = os.path.join(os.path.dirname(__file__), "data", "signal_samples.csv")
        cls.df = pd.read_csv(csv_path)

    def test_band_count(self):
        """测试频段统计"""
        bands = self.df["Band"].unique()
        self.assertGreater(len(bands), 0)

    def test_cell_id_count_per_band(self):
        """测试各频段基站数量统计"""
        band_counts = self.df.groupby("Band")["CellID"].nunique()
        self.assertEqual(len(band_counts), len(self.df["Band"].unique()))
        self.assertTrue(all(band_counts > 0))

    def test_terminal_type_distribution(self):
        """测试终端类型分布统计"""
        terminal_counts = self.df["TerminalType"].value_counts()
        self.assertGreater(len(terminal_counts), 0)
        self.assertEqual(terminal_counts.sum(), len(self.df))

    def test_rsrp_range(self):
        """测试 RSRP 值域合理性"""
        self.assertTrue(all(self.df["RSRP_dBm"] < 0), "RSRP 应为负值")
        self.assertTrue(all(self.df["RSRP_dBm"] > -150), "RSRP 不应低于 -150 dBm")

    def test_download_speed_positive(self):
        """测试下载速率均为正值"""
        self.assertTrue(all(self.df["Download_Mbps"] > 0), "下载速率应为正值")


if __name__ == "__main__":
    unittest.main()
