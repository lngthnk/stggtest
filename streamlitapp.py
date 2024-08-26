# streamlit_app.py

import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Create a connection object for the first spreadsheet
conn_one = st.connection("gsheets1", type=GSheetsConnection)
df_one = conn_one.read()


# Create a connection object for the second spreadsheet
conn_two = st.connection("gsheets2", type=GSheetsConnection)
df_two = conn_two.read()
st.header('df1')
st.dataframe(df_one)
st.header('df2')
st.dataframe(df_two)