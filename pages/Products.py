import streamlit as st
import pandas as pd
from db import products_col

st.set_page_config(page_title="Products", layout="wide")

# ----------------------------
# Page Styling
# ----------------------------
st.markdown("""
<style>
    .main, .block-container {
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

    .product-card {
        background: linear-gradient(135deg, #0f172a, #111827);
        border: 1px solid #1f2937;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.14);
    }

    .product-title {
        font-size: 24px;
        font-weight: 700;
        color: white;
        margin-bottom: 4px;
    }

    .product-sub {
        color: #9ca3af;
        font-size: 14px;
        margin-bottom: 14px;
    }

    .tag-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 14px;
    }

    .tag {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: #1f2937;
        color: #e5e7eb;
        font-size: 12px;
        border: 1px solid #374151;
    }

    .cost-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-top: 10px;
    }

    .cost-box {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 14px;
        text-align: center;
    }

    .cost-label {
        font-size: 12px;
        color: #9ca3af;
        margin-bottom: 4px;
    }

    .cost-value {
        font-size: 18px;
        font-weight: 700;
        color: white;
    }

    @media (max-width: 900px) {
        .cost-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Data Load
# ----------------------------
products_data = list(products_col.find({}, {"_id": 0}))
products = pd.DataFrame(products_data)

# ----------------------------
# Header
# ----------------------------
st.title("Products Dashboard")
st.caption("Explore product categories, harvest cycles, shelf life, and operational cost structure across export-ready products.")

# ----------------------------
# Empty State
# ----------------------------
if products.empty:
    st.warning("No product data found in MongoDB. Insert data into the products collection to view analytics.")
    st.stop()

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")

categories = ["All"] + sorted(products["category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", categories)

states = ["All"] + sorted(products["origin_state"].dropna().unique().tolist())
selected_state = st.sidebar.selectbox("Select Origin State", states)

grades = ["All"] + sorted(products["quality_grade"].dropna().unique().tolist())
selected_grade = st.sidebar.selectbox("Select Quality Grade", grades)

filtered = products.copy()

if selected_category != "All":
    filtered = filtered[filtered["category"] == selected_category]

if selected_state != "All":
    filtered = filtered[filtered["origin_state"] == selected_state]

if selected_grade != "All":
    filtered = filtered[filtered["quality_grade"] == selected_grade]

# ----------------------------
# KPI Cards
# ----------------------------
col1, col2, col3, col4 = st.columns(4)

avg_shelf = round(filtered["shelf_life"].mean(), 1)
fresh_count = filtered[filtered["category"] == "Fresh Fruits"].shape[0]
dry_count = filtered[filtered["category"] == "Dry Fruits"].shape[0]
spice_count = filtered[filtered["category"] == "Spices"].shape[0]

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Products</div><div class="metric-value">{filtered.shape[0]}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Avg Shelf Life</div><div class="metric-value">{avg_shelf} d</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Fresh Fruits</div><div class="metric-value">{fresh_count}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Dry Fruits / Spices</div><div class="metric-value">{dry_count + spice_count}</div></div>', unsafe_allow_html=True)

st.markdown("")

# ----------------------------
# Product Cards
# ----------------------------
st.markdown('<div class="section-title">Product Overview</div>', unsafe_allow_html=True)
st.caption("Detailed product profiles with category, origin, seasonality, and operational cost structure.")

for _, row in filtered.iterrows():
    harvest = ", ".join(row["harvest_season"]) if isinstance(row["harvest_season"], list) else row["harvest_season"]
    cost = row["cost_structure"]

    st.markdown(f"""
        <div class="product-card">
            <div class="product-title">{row['name']}</div>
            <div class="product-sub">{row['category']} • Origin: {row['origin_state']}</div>

            <div class="tag-wrap">
                <span class="tag">Grade: {row['quality_grade']}</span>
                <span class="tag">Shelf Life: {row['shelf_life']} days</span>
                <span class="tag">Harvest: {harvest}</span>
            </div>

            <div class="cost-grid">
                <div class="cost-box">
                    <div class="cost-label">Production Cost</div>
                    <div class="cost-value">₹{cost['production_cost_per_kg']}/kg</div>
                </div>
                <div class="cost-box">
                    <div class="cost-label">Packaging Cost</div>
                    <div class="cost-value">₹{cost['packaging_cost_per_kg']}/kg</div>
                </div>
                <div class="cost-box">
                    <div class="cost-label">Handling Cost</div>
                    <div class="cost-value">₹{cost['handling_cost_per_kg']}/kg</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ----------------------------
# Detailed Table
# ----------------------------
st.markdown('<div class="section-title">Detailed Product Data</div>', unsafe_allow_html=True)
st.caption("Structured product-level dataset for detailed inspection and export analysis.")

table_df = filtered.copy()
table_df["harvest_season"] = table_df["harvest_season"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

st.dataframe(table_df, use_container_width=True, hide_index=True)