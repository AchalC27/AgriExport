import streamlit as st
import pandas as pd
import plotly.express as px
from db import products_col, markets_col, logistics_col

st.set_page_config(page_title="Profitability", layout="wide")

# ----------------------------
# Page Styling
# ----------------------------
st.markdown("""
    <style>
        .main {
            padding-top: 1rem;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #111827, #1f2937);
            padding: 18px;
            border-radius: 16px;
            border: 1px solid #374151;
            box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        }
        .metric-title {
            font-size: 14px;
            color: #9ca3af;
            margin-bottom: 6px;
        }
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: white;
        }
        .section-title {
            font-size: 22px;
            font-weight: 700;
            margin-top: 10px;
            margin-bottom: 10px;
        }
        .insight-card {
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 18px;
            padding: 18px;
            margin-bottom: 14px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        }
        .insight-title {
            font-size: 18px;
            font-weight: 700;
            color: white;
            margin-bottom: 8px;
        }
        .tag {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            background: #1f2937;
            color: #e5e7eb;
            font-size: 12px;
            margin-right: 6px;
            margin-bottom: 6px;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Load Data
# ----------------------------
products = pd.DataFrame(list(products_col.find({}, {"_id": 0})))
markets = pd.DataFrame(list(markets_col.find({}, {"_id": 0})))
logistics = pd.DataFrame(list(logistics_col.find({}, {"_id": 0})))

# ----------------------------
# Empty State
# ----------------------------
if products.empty or markets.empty or logistics.empty:
    st.warning("Required data is missing in MongoDB. Ensure products, markets, and logistics collections are populated.")
    st.stop()

# ----------------------------
# Prepare Product Cost
# ----------------------------
products["base_cost"] = products["cost_structure"].apply(
    lambda x: x["production_cost_per_kg"] + x["packaging_cost_per_kg"] + x["handling_cost_per_kg"]
)

# Synthetic selling price based on category
category_markup = {
    "Fresh Fruits": 1.8,
    "Dry Fruits": 1.45,
    "Spices": 1.65
}
products["selling_price"] = products.apply(
    lambda row: round(row["base_cost"] * category_markup.get(row["category"], 1.5), 2), axis=1
)

# Cross Join Products x Markets
products["key"] = 1
markets["key"] = 1
profit_df = pd.merge(products, markets, on="key").drop("key", axis=1)

# Merge Logistics
profit_df = profit_df.merge(
    logistics,
    left_on="country_name",
    right_on="destination_country",
    how="left"
)

# Profit Calculations
profit_df["tariff_cost"] = (profit_df["selling_price"] * profit_df["tariff_structure"]) / 100
profit_df["total_cost"] = profit_df["base_cost"] + profit_df["shipping_cost_per_kg"] + profit_df["tariff_cost"]
profit_df["profit_per_kg"] = (profit_df["selling_price"] - profit_df["total_cost"]).round(2)
profit_df["margin_percent"] = ((profit_df["profit_per_kg"] / profit_df["selling_price"]) * 100).round(2)

# Clean View
profit_df = profit_df[[
    "name", "category", "country_name", "region",
    "selling_price", "base_cost", "shipping_cost_per_kg",
    "tariff_cost", "total_cost", "profit_per_kg", "margin_percent"
]]

profit_df.columns = [
    "Product", "Category", "Country", "Region",
    "Selling Price", "Base Cost", "Shipping Cost",
    "Tariff Cost", "Total Cost", "Profit per Kg", "Margin %"
]

# ----------------------------
# Header
# ----------------------------
st.title("Profitability Dashboard")
st.caption("Analyze profitability across all product-country combinations using dynamic cost, tariff, and logistics calculations.")

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")

products_filter = ["All"] + sorted(profit_df["Product"].unique().tolist())
selected_product = st.sidebar.selectbox("Select Product", products_filter)

regions_filter = ["All"] + sorted(profit_df["Region"].unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", regions_filter)

filtered = profit_df.copy()

if selected_product != "All":
    filtered = filtered[filtered["Product"] == selected_product]

if selected_region != "All":
    filtered = filtered[filtered["Region"] == selected_region]

# ----------------------------
# KPI Cards
# ----------------------------
col1, col2, col3, col4 = st.columns(4)

avg_profit = round(filtered["Profit per Kg"].mean(), 2)
avg_margin = round(filtered["Margin %"].mean(), 2)
top_combo = filtered.loc[filtered["Profit per Kg"].idxmax()]
low_margin_count = filtered[filtered["Margin %"] < 10].shape[0]

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Combinations</div><div class="metric-value">{filtered.shape[0]}</div></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Avg Profit / Kg</div><div class="metric-value">₹{avg_profit}</div></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Avg Margin</div><div class="metric-value">{avg_margin}%</div></div>', unsafe_allow_html=True)

with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Low Margin Cases</div><div class="metric-value">{low_margin_count}</div></div>', unsafe_allow_html=True)

st.markdown("")

# ----------------------------
# Charts
# ----------------------------
left, right = st.columns(2)

with left:
    st.markdown('<div class="section-title">Top 15 Profitable Markets</div>', unsafe_allow_html=True)
    top_chart = filtered.sort_values("Profit per Kg", ascending=False).head(15)
    fig_profit = px.bar(
        top_chart,
        x="Country",
        y="Profit per Kg",
        color="Category",
        hover_data=["Product"],
        text="Profit per Kg"
    )
    fig_profit.update_layout(height=420)
    st.plotly_chart(fig_profit, use_container_width=True)

with right:
    st.markdown('<div class="section-title">Margin Distribution</div>', unsafe_allow_html=True)
    fig_margin = px.histogram(
        filtered,
        x="Margin %",
        nbins=20,
        color="Category"
    )
    fig_margin.update_layout(height=420)
    st.plotly_chart(fig_margin, use_container_width=True)

# ----------------------------
# Insights
# ----------------------------
st.markdown('<div class="section-title">Key Insights</div>', unsafe_allow_html=True)

top3 = filtered.sort_values("Profit per Kg", ascending=False).head(3)
low3 = filtered.sort_values("Margin %", ascending=True).head(3)

colA, colB = st.columns(2)

with colA:
    st.markdown('<div class="insight-title">Top 3 Profitable Combinations</div>', unsafe_allow_html=True)
    for _, row in top3.iterrows():
        st.markdown(f"""
            <div class="insight-card">
                <span class="tag">{row['Product']}</span>
                <span class="tag">{row['Country']}</span>
                <span class="tag">₹{row['Profit per Kg']}/kg</span>
                <span class="tag">{row['Margin %']}% Margin</span>
            </div>
        """, unsafe_allow_html=True)

with colB:
    st.markdown('<div class="insight-title">Low Margin / Risky Combinations</div>', unsafe_allow_html=True)
    for _, row in low3.iterrows():
        st.markdown(f"""
            <div class="insight-card">
                <span class="tag">{row['Product']}</span>
                <span class="tag">{row['Country']}</span>
                <span class="tag">₹{row['Profit per Kg']}/kg</span>
                <span class="tag">{row['Margin %']}% Margin</span>
            </div>
        """, unsafe_allow_html=True)

# ----------------------------
# Detailed Table
# ----------------------------
st.markdown('<div class="section-title">Detailed Profitability Matrix</div>', unsafe_allow_html=True)
st.caption("Dynamic profitability matrix across all product-country combinations.")

st.dataframe(filtered, use_container_width=True, hide_index=True)