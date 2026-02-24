
# =========================================================
# 🍽️ Multi-Channel Restaurant Profitability Dashboard
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------
# Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Restaurant Channel Profitability",
    layout="wide"
)

st.title("🍽️ Multi-Channel Profitability Dashboard")
st.caption("Cost Structure & Channel Margin Analysis")

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("SkyCity Auckland Restaurants & Bars.csv")
    return df

df = load_data()

# ---------------------------------------------------------
# Recalculate Core Metrics (DO NOT trust provided profits)
# ---------------------------------------------------------

# ---------- COGS ----------
df["COGS_InStore"] = df["InStoreRevenue"] * df["COGSRate"]
df["COGS_UE"] = df["UberEatsRevenue"] * df["COGSRate"]
df["COGS_DD"] = df["DoorDashRevenue"] * df["COGSRate"]
df["COGS_SD"] = df["SelfDeliveryRevenue"] * df["COGSRate"]

# ---------- OPEX ----------
df["OPEX_InStore"] = df["InStoreRevenue"] * df["OPEXRate"]
df["OPEX_UE"] = df["UberEatsRevenue"] * df["OPEXRate"]
df["OPEX_DD"] = df["DoorDashRevenue"] * df["OPEXRate"]
df["OPEX_SD"] = df["SelfDeliveryRevenue"] * df["OPEXRate"]

# ---------- Commission ----------
df["Commission_UE"] = df["UberEatsRevenue"] * df["CommissionRate"]
df["Commission_DD"] = df["DoorDashRevenue"] * df["CommissionRate"]

# ---------- Net Profit ----------
df["Calc_InStoreProfit"] = (
    df["InStoreRevenue"]
    - df["COGS_InStore"]
    - df["OPEX_InStore"]
)

df["Calc_UE_Profit"] = (
    df["UberEatsRevenue"]
    - df["COGS_UE"]
    - df["OPEX_UE"]
    - df["Commission_UE"]
)

df["Calc_DD_Profit"] = (
    df["DoorDashRevenue"]
    - df["COGS_DD"]
    - df["OPEX_DD"]
    - df["Commission_DD"]
)

df["Calc_SD_Profit"] = (
    df["SelfDeliveryRevenue"]
    - df["COGS_SD"]
    - df["OPEX_SD"]
    - df["SD_DeliveryTotalCost"]
)

# ---------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------
st.sidebar.header("🔎 Filters")

cuisine_filter = st.sidebar.multiselect(
    "Select Cuisine",
    df["CuisineType"].unique(),
    default=df["CuisineType"].unique()
)

segment_filter = st.sidebar.multiselect(
    "Select Segment",
    df["Segment"].unique(),
    default=df["Segment"].unique()
)

# What-if sliders
commission_adj = st.sidebar.slider(
    "Commission Rate Adjustment",
    -0.10, 0.10, 0.0, 0.01
)

delivery_adj = st.sidebar.slider(
    "Self-Delivery Cost Adjustment",
    -5.0, 5.0, 0.0, 0.5
)

# ---------------------------------------------------------
# Apply Filters
# ---------------------------------------------------------
filtered_df = df[
    (df["CuisineType"].isin(cuisine_filter)) &
    (df["Segment"].isin(segment_filter))
].copy()

# ---------------------------------------------------------
# What-If Logic
# ---------------------------------------------------------
filtered_df["Adj_CommissionRate"] = (
    filtered_df["CommissionRate"] + commission_adj
).clip(lower=0)

filtered_df["Adj_UE_Profit"] = (
    filtered_df["UberEatsRevenue"]
    - filtered_df["COGS_UE"]
    - filtered_df["OPEX_UE"]
    - filtered_df["UberEatsRevenue"] * filtered_df["Adj_CommissionRate"]
)

filtered_df["Adj_SD_Profit"] = (
    filtered_df["SelfDeliveryRevenue"]
    - filtered_df["COGS_SD"]
    - filtered_df["OPEX_SD"]
    - (filtered_df["SD_DeliveryTotalCost"] + delivery_adj)
)

# ---------------------------------------------------------
# KPI Row
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "In-Store Profit",
    f"${filtered_df['Calc_InStoreProfit'].sum():,.0f}"
)

col2.metric(
    "Uber Eats Profit",
    f"${filtered_df['Adj_UE_Profit'].sum():,.0f}"
)

col3.metric(
    "DoorDash Profit",
    f"${filtered_df['Calc_DD_Profit'].sum():,.0f}"
)

col4.metric(
    "Self Delivery Profit",
    f"${filtered_df['Adj_SD_Profit'].sum():,.0f}"
)

# ---------------------------------------------------------
# Channel Comparison Chart
# ---------------------------------------------------------
st.subheader("📊 Profit by Channel")

channel_profit = {
    "InStore": filtered_df["Calc_InStoreProfit"].sum(),
    "UberEats": filtered_df["Adj_UE_Profit"].sum(),
    "DoorDash": filtered_df["Calc_DD_Profit"].sum(),
    "SelfDelivery": filtered_df["Adj_SD_Profit"].sum(),
}

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(channel_profit.keys(), channel_profit.values())
ax.set_title("Channel Profit Comparison")

st.pyplot(fig)

# ---------------------------------------------------------
# Cuisine Heatmap
# ---------------------------------------------------------
st.subheader("Margin Heatmap by Cuisine")

filtered_df["Margin_UE"] = (
    filtered_df["Adj_UE_Profit"] / filtered_df["UberEatsRevenue"]
)

pivot_margin = filtered_df.pivot_table(
    values="Margin_UE",
    index="CuisineType",
    columns="Segment",
    aggfunc="mean"
)

fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.heatmap(pivot_margin, annot=True, fmt=".2f", cmap="RdYlGn", ax=ax2)

st.pyplot(fig2)

# =========================================================
# END OF APP
# =========================================================

# =========================================================
#  EXECUTIVE INSIGHTS PANEL (ADD BELOW HEATMAP)
# =========================================================

st.subheader("🧠 Executive Insights")

total_profits = {
    "InStore": filtered_df["Calc_InStoreProfit"].sum(),
    "UberEats": filtered_df["Adj_UE_Profit"].sum(),
    "DoorDash": filtered_df["Calc_DD_Profit"].sum(),
    "SelfDelivery": filtered_df["Adj_SD_Profit"].sum(),
}

best_channel = max(total_profits, key=total_profits.get)
worst_channel = min(total_profits, key=total_profits.get)

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.success(f"✅ Most profitable channel: **{best_channel}**")

with insight_col2:
    st.error(f"⚠️ Lowest performing channel: **{worst_channel}**")

# Commission pressure indicator
commission_share = (
    filtered_df["Commission_UE"].sum() /
    max(filtered_df["UberEatsRevenue"].sum(), 1)
)

if commission_share > 0.25:
    st.warning("🚨 High commission pressure detected on aggregator channels.")
else:
    st.info("👍 Commission levels appear within sustainable range.")

# =========================================================
# ⭐ TOP & BOTTOM PERFORMERS TABLE
# =========================================================

st.subheader("🏆 Top & Bottom Restaurants (Uber Eats Margin)")

filtered_df["Margin_UE"] = (
    filtered_df["Adj_UE_Profit"] / filtered_df["UberEatsRevenue"]
)

top_restaurants = filtered_df.nlargest(
    5, "Margin_UE"
)[["RestaurantName", "CuisineType", "Margin_UE"]]

bottom_restaurants = filtered_df.nsmallest(
    5, "Margin_UE"
)[["RestaurantName", "CuisineType", "Margin_UE"]]

tab1, tab2 = st.tabs(["Top Performers", "Bottom Performers"])

with tab1:
    st.dataframe(top_restaurants, use_container_width=True)

with tab2:
    st.dataframe(bottom_restaurants, use_container_width=True)

# =========================================================
# ⭐ FOOTER
# =========================================================

st.markdown("---")
st.caption(
    "Built for multi-channel unit economics analysis • Streamlit Dashboard"
)
