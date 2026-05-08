import pandas as pd
import pytest


def test_load_data():
    df = pd.read_csv("data/signal_samples.csv")
    assert len(df) > 0
    assert "Latitude" in df.columns
    assert "Longitude" in df.columns
    assert "Band" in df.columns
    assert "RSRP_dBm" in df.columns
    assert "TerminalType" in df.columns
    assert "Download_Mbps" in df.columns


def test_rsrp_color_logic():
    def get_color(rsrp):
        if rsrp > -90:
            return [0, 255, 0]
        elif rsrp < -110:
            return [255, 0, 0]
        else:
            return [255, 165, 0]

    assert get_color(-80) == [0, 255, 0]
    assert get_color(-120) == [255, 0, 0]
    assert get_color(-100) == [255, 165, 0]


def test_filter_by_band():
    df = pd.read_csv("data/signal_samples.csv")
    filtered = df[df["Band"].isin(["n28"])]
    assert all(filtered["Band"] == "n28")


def test_filter_by_rsrp():
    df = pd.read_csv("data/signal_samples.csv")
    filtered = df[(df["RSRP_dBm"] >= -100) & (df["RSRP_dBm"] <= -90)]
    assert all(filtered["RSRP_dBm"] >= -100)
    assert all(filtered["RSRP_dBm"] <= -90)


def test_band_counts():
    df = pd.read_csv("data/signal_samples.csv")
    band_counts = df["Band"].value_counts()
    assert len(band_counts) > 0
    assert band_counts.sum() == len(df)


def test_terminal_type_counts():
    df = pd.read_csv("data/signal_samples.csv")
    terminal_counts = df["TerminalType"].value_counts()
    assert len(terminal_counts) > 0
    assert terminal_counts.sum() == len(df)


def test_filter_by_terminal():
    df = pd.read_csv("data/signal_samples.csv")
    filtered = df[df["TerminalType"].isin(["Smartphone"])]
    assert all(filtered["TerminalType"] == "Smartphone")


def test_filter_by_download():
    df = pd.read_csv("data/signal_samples.csv")
    filtered = df[(df["Download_Mbps"] >= 100) & (df["Download_Mbps"] <= 500)]
    assert all(filtered["Download_Mbps"] >= 100)
    assert all(filtered["Download_Mbps"] <= 500)


def test_combined_filter():
    df = pd.read_csv("data/signal_samples.csv")
    filtered = df[
        (df["Band"].isin(["n28"])) &
        (df["TerminalType"].isin(["Smartphone"])) &
        (df["RSRP_dBm"] >= -100)
        ]
    assert all(filtered["Band"] == "n28")
    assert all(filtered["TerminalType"] == "Smartphone")
    assert all(filtered["RSRP_dBm"] >= -100)


def test_data_statistics():
    df = pd.read_csv("data/signal_samples.csv")
    assert df["RSRP_dBm"].min() < df["RSRP_dBm"].max()
    assert df["Download_Mbps"].min() >= 0


def test_unique_bands():
    df = pd.read_csv("data/signal_samples.csv")
    bands = df["Band"].unique()
    assert len(bands) > 0
    assert "n28" in bands or "n41" in bands or "n78" in bands


def test_unique_terminals():
    df = pd.read_csv("data/signal_samples.csv")
    terminals = df["TerminalType"].unique()
    assert len(terminals) > 0


def test_latitude_range():
    df = pd.read_csv("data/signal_samples.csv")
    assert df["Latitude"].min() > 0
    assert df["Latitude"].max() < 90


def test_longitude_range():
    df = pd.read_csv("data/signal_samples.csv")
    assert df["Longitude"].min() > 100
    assert df["Longitude"].max() < 130


def test_sinr_exists():
    df = pd.read_csv("data/signal_samples.csv")
    assert "SINR_dB" in df.columns


def test_cellid_exists():
    df = pd.read_csv("data/signal_samples.csv")
    assert "CellID" in df.columns
    assert df["CellID"].nunique() > 0