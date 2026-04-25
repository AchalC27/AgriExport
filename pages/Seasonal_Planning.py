import streamlit as st
import pandas as pd

st.title("Seasonal Export Planning")

data = {
    "Product": ["Alphonso Mango", "Grapes", "Pomegranate", "Cashew", "Turmeric"],
    "Harvest Season": ["Mar-May", "Jan-Mar", "Jul-Sep", "Feb-Apr", "Jan-Feb"],
    "Best Export Countries": ["UAE, Singapore", "UAE, Germany", "Singapore, UAE", "USA, UK", "Germany, Singapore"]
}

df = pd.DataFrame(data)

st.dataframe(df, use_container_width=True)