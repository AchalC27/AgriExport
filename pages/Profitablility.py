import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Profitability Analysis")

data = {
    "Country": ["UAE", "UK", "USA", "Germany", "Singapore", "Canada"],
    "Profit_per_kg": [52, 64, 75, 48, 58, 35]
}

df = pd.DataFrame(data)

fig = px.bar(df, x="Country", y="Profit_per_kg", title="Profit per Kg by Country")
st.plotly_chart(fig, use_container_width=True)

st.dataframe(df, use_container_width=True)