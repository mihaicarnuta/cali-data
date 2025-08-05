import streamlit as st
import pandas as pd

st.set_page_config(page_title="CaliData App", layout="wide")

st.title("Inspect SMS Data")

# Load the Parquet file from the parent directory
df = pd.read_parquet("all_sms_data.parquet")

st.subheader("Data Preview")
st.dataframe(df.head(20))

st.subheader("Column Data Types")
# Display ftypes (use dtypes if ftypes is not available in newer pandas)

st.write(df.dtypes)

st.subheader("Shape of the Data")
st.write(f"{df.shape[0]:,} rows × {df.shape[1]:,} columns")