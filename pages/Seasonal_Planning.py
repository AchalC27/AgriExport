import streamlit as st
import pandas as pd
import plotly.express as px
from db import products_col, markets_col, logistics_col

st.set_page_config(page_title="Seasonal Planning", layout="wide")

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
        .season-card {
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 18px;
            padding: 18px;
            margin-bottom: 14px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        }
        .season-title {
            font-size: 20px;
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
# Prepare Seasonal Dataset
# ----------------------------
month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

products["Peak Months"] = products["harvest_season"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
products["Harvest Window"] = products["harvest_season"].apply(lambda x: f"{x[0]} - {x[-1]}" if isinstance(x, list) else x)

# Demand + transit scoring
market_score = {"High": 3, "Medium": 2, "Low": 1}
markets["Demand Score"] = markets["demand_level"].map(market_score)

season_df = products.assign(key=1).merge(markets.assign(key=1), on="key").drop("key", axis=1)
season_df = season_df.merge(logistics, left_on="country_name", right_on="destination_country", how="left")

# Ranking logic
season_df["Transit Score"] = season_df["transit_days"].apply(lambda x: 3 if x <= 3 else (2 if x <= 6 else 1))
season_df["Export Score"] = season_df["Demand Score"] + season_df["Transit Score"]

# Top 2 best countries for each product
best_markets = (
    season_df.sort_values(["name", "Export Score"], ascending=[True, False])
    .groupby("name")
    .head(2)
    .groupby("name")["country_name"]
    .apply(lambda x: ", ".join(x))
    .reset_index()
)

best_markets.columns = ["name", "Best Markets"]

# Merge final seasonal dataset
season_final = products.merge(best_markets, on="name", how="left")
season_final["Demand Level"] = season_final["name"].map(
    season_df.groupby("name")["demand_level"].agg(lambda x: x.mode()[0])
)
season_final["Transit Risk"] = season_final["name"].map(
    season_df.groupby("name")["transit_days"].mean().apply(lambda x: "Low" if x <= 4 else ("Medium" if x <= 8 else "High"))
)

season_final = season_final[["name", "category", "Harvest Window", "Peak Months", "Best Markets", "Demand Level", "Transit Risk"]]
season_final.columns = ["Product", "Category", "Harvest Window", "Peak Months", "Best Markets", "Demand Level", "Transit Risk"]

# ----------------------------
# Header
# ----------------------------
st.title("Seasonal Export Planning Dashboard")
st.caption("Plan exports based on harvest season, demand patterns, and logistics efficiency across global markets.")

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")

product_filter = ["All"] + sorted(season_final["Product"].unique().tolist())
selected_product = st.sidebar.selectbox("Select Product", product_filter)

category_filter = ["All"] + sorted(season_final["Category"].unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", category_filter)

filtered = season_final.copy()

if selected_product != "All":
    filtered = filtered[filtered["Product"] == selected_product]

if selected_category != "All":
    filtered = filtered[filtered["Category"] == selected_category]

# ----------------------------
# KPI Cards
# ----------------------------
col1, col2, col3, col4 = st.columns(4)

high_demand = filtered[filtered["Demand Level"] == "High"].shape[0]
low_risk = filtered[filtered["Transit Risk"] == "Low"].shape[0]
readiness = round((low_risk / filtered.shape[0]) * 100, 0) if filtered.shape[0] > 0 else 0

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Products Planned</div><div class="metric-value">{filtered.shape[0]}</div></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">High Demand Products</div><div class="metric-value">{high_demand}</div></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Low Transit Risk</div><div class="metric-value">{low_risk}</div></div>', unsafe_allow_html=True)

with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Export Readiness</div><div class="metric-value">{readiness}%</div></div>', unsafe_allow_html=True)

st.markdown("")

# ----------------------------
# Charts
# ----------------------------
left, right = st.columns(2)

with left:
    st.markdown('<div class="section-title">Demand Level by Product</div>', unsafe_allow_html=True)
    demand_count = filtered["Demand Level"].value_counts().reset_index()
    demand_count.columns = ["Demand Level", "Count"]

    fig_demand = px.bar(
        demand_count,
        x="Demand Level",
        y="Count",
        text="Count"
    )
    fig_demand.update_layout(height=420)
    st.plotly_chart(fig_demand, use_container_width=True)

with right:
    st.markdown('<div class="section-title">Transit Risk Distribution</div>', unsafe_allow_html=True)
    risk_count = filtered["Transit Risk"].value_counts().reset_index()
    risk_count.columns = ["Transit Risk", "Count"]

    fig_risk = px.pie(
        risk_count,
        names="Transit Risk",
        values="Count",
        hole=0.45
    )
    fig_risk.update_layout(height=420)
    st.plotly_chart(fig_risk, use_container_width=True)

# ----------------------------
# Seasonal Recommendation Cards
# ----------------------------
st.markdown('<div class="section-title">Seasonal Export Recommendations</div>', unsafe_allow_html=True)

for _, row in filtered.iterrows():
    st.markdown(f"""
        <div class="season-card">
            <div class="season-title">{row['Product']}</div>
            <span class="tag">{row['Category']}</span>
            <span class="tag">Harvest: {row['Harvest Window']}</span>
            <span class="tag">Peak: {row['Peak Months']}</span>
            <span class="tag">Best Markets: {row['Best Markets']}</span>
            <span class="tag">Demand: {row['Demand Level']}</span>
            <span class="tag">Transit Risk: {row['Transit Risk']}</span>
        </div>
    """, unsafe_allow_html=True)

# ----------------------------
# Detailed Table
# ----------------------------
st.markdown('<div class="section-title">Seasonal Planning Matrix</div>', unsafe_allow_html=True)
st.caption("Dynamic seasonal export schedule based on harvest window, market demand, and logistics suitability.")

st.dataframe(filtered, use_container_width=True, hide_index=True)