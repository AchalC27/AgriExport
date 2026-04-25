import streamlit as st
import pandas as pd
from db import products_col

st.title("Products")

products = pd.DataFrame(list(products_col.find({}, {"_id": 0})))

category = st.selectbox("Filter by Category", ["All"] + list(products["category"].unique()))

if category != "All":
    products = products[products["category"] == category]

st.dataframe(products, use_container_width=True)