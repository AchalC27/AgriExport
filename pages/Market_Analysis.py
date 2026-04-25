import streamlit as st
import pandas as pd
from db import markets_col
import plotly.express as px

st.title("Market Analysis")

# Fetch data
markets_data = list(markets_col.find({}, {"_id": 0}))

# Debug output
st.write("Raw MongoDB Data:", markets_data)

markets = pd.DataFrame(markets_data)

# Debug DataFrame
st.write("DataFrame Columns:", markets.columns.tolist())
st.write("DataFrame Preview:", markets)

if markets.empty:
    st.error("No market data found in MongoDB. Please insert data into the markets collection.")
else:
    fig = px.bar(
        markets,
        x="country_name",
        y="tariff_structure",
        color="demand_level",
        title="Country-wise Tariff Structure"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(markets, use_container_width=True)