# streamlit_app.py

import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Create a connection object for the first spreadsheet
conn_one = st.connection("gsheets", type=GSheetsConnection)
df_one = conn_one.read()


# Create a connection object for the second spreadsheet
conn_two = st.connection("df2", type=GSheetsConnection)
df_two = conn_two.read()
st.header('df1')
st.dataframe(df_one.tail())
st.header('df2')
st.dataframe(df_two.tail())