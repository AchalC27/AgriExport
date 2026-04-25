import streamlit as st
import pandas as pd
from db import products_col, markets_col, logistics_col

st.set_page_config(page_title="AgriExport Dashboard", layout="wide")

st.title("AgriExport Solutions Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Total Products", products_col.count_documents({}))
col2.metric("Total Markets", markets_col.count_documents({}))
col3.metric("Logistics Routes", logistics_col.count_documents({}))

st.markdown("---")

st.subheader("Export Market Analysis Overview")

products = pd.DataFrame(list(products_col.find({}, {"_id": 0})))
st.dataframe(products, use_container_width=True)