# dashboard/app.py

import streamlit as st
import pandas as pd
import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="adaptive_bi",
    user="bi_user",
    password="bi_pass",
    host="localhost",
    port="5432"
)

query = "SELECT * FROM orders ORDER BY timestamp DESC LIMIT 10;"
df = pd.read_sql(query, conn)

st.title("Adaptive BI Dashboard")
st.subheader("Recent Orders")
st.dataframe(df)

conn.close()
