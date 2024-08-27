# streamlit_app.py

import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Create a connection object for the first spreadsheet
conn_one = st.connection("name_one", type=GSheetsConnection)
df_one = conn_one.read()


# Create a connection object for the second spreadsheet
conn_two = st.connection("name_two", type=GSheetsConnection)
df_two = conn_two.read()

st.dataframe(df_one.tail())
st.data_editor(df_two.tail())