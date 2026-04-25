import streamlit as st
import pandas as pd
import plotly.express as px
from db import markets_col

st.set_page_config(page_title="Market Analysis", layout="wide")

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
            background-color: #111827;
            padding: 18px;
            border-radius: 14px;
            border: 1px solid #1f2937;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
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
        .subtle {
            color: #6b7280;
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Data Load
# ----------------------------
markets_data = list(markets_col.find({}, {"_id": 0}))
markets = pd.DataFrame(markets_data)

# ----------------------------
# Header
# ----------------------------
st.title("Market Analysis Dashboard")
st.caption("Analyze tariffs, demand levels, exchange rates, and market preferences across export destinations.")

# ----------------------------
# Empty State
# ----------------------------
if markets.empty:
    st.warning("No market data found in MongoDB. Insert data into the markets collection to view analytics.")
    st.stop()

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")

regions = ["All"] + sorted(markets["region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", regions)

demand_levels = ["All"] + sorted(markets["demand_level"].dropna().unique().tolist())
selected_demand = st.sidebar.selectbox("Select Demand Level", demand_levels)

filtered = markets.copy()

if selected_region != "All":
    filtered = filtered[filtered["region"] == selected_region]

if selected_demand != "All":
    filtered = filtered[filtered["demand_level"] == selected_demand]

# ----------------------------
# KPI Cards
# ----------------------------
col1, col2, col3, col4 = st.columns(4)

avg_tariff = round(filtered["tariff_structure"].mean(), 2)
avg_exchange = round(filtered["exchange_rate_to_inr"].mean(), 2)
high_demand_count = filtered[filtered["demand_level"] == "High"].shape[0]
premium_pref = filtered[filtered["preferred_quality"] == "Premium"].shape[0]

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Markets</div>
            <div class="metric-value">{filtered.shape[0]}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Tariff (%)</div>
            <div class="metric-value">{avg_tariff}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Exchange Rate</div>
            <div class="metric-value">{avg_exchange}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">High Demand Markets</div>
            <div class="metric-value">{high_demand_count}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ----------------------------
# Charts Row
# ----------------------------
left, right = st.columns(2)

with left:
    st.markdown('<div class="section-title">Tariff Structure by Country</div>', unsafe_allow_html=True)
    fig_tariff = px.bar(
        filtered,
        x="country_name",
        y="tariff_structure",
        color="demand_level",
        text="tariff_structure"
    )
    fig_tariff.update_layout(
        xaxis_title="Country",
        yaxis_title="Tariff (%)",
        height=420,
        legend_title="Demand Level"
    )
    st.plotly_chart(fig_tariff, use_container_width=True)

with right:
    st.markdown('<div class="section-title">Demand Distribution</div>', unsafe_allow_html=True)
    demand_count = filtered["demand_level"].value_counts().reset_index()
    demand_count.columns = ["Demand Level", "Count"]

    fig_demand = px.pie(
        demand_count,
        names="Demand Level",
        values="Count",
        hole=0.45
    )
    fig_demand.update_layout(height=420)
    st.plotly_chart(fig_demand, use_container_width=True)

# ----------------------------
# Secondary Charts
# ----------------------------
left2, right2 = st.columns(2)

with left2:
    st.markdown('<div class="section-title">Exchange Rate Comparison</div>', unsafe_allow_html=True)
    fig_fx = px.line(
        filtered.sort_values("exchange_rate_to_inr"),
        x="country_name",
        y="exchange_rate_to_inr",
        markers=True
    )
    fig_fx.update_layout(
        xaxis_title="Country",
        yaxis_title="Exchange Rate to INR",
        height=400
    )
    st.plotly_chart(fig_fx, use_container_width=True)

with right2:
    st.markdown('<div class="section-title">Preferred Quality Split</div>', unsafe_allow_html=True)
    quality_count = filtered["preferred_quality"].value_counts().reset_index()
    quality_count.columns = ["Preferred Quality", "Count"]

    fig_quality = px.bar(
        quality_count,
        x="Preferred Quality",
        y="Count",
        text="Count"
    )
    fig_quality.update_layout(height=400)
    st.plotly_chart(fig_quality, use_container_width=True)

# ----------------------------
# Detailed Table
# ----------------------------
st.markdown('<div class="section-title">Detailed Market Data</div>', unsafe_allow_html=True)
st.caption("Country-wise market information with tariffs, currency, demand, and preferred quality.")

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)