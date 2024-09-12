# streamlit_app.py

import streamlit as st
from streamlit_gsheets import GSheetsConnection
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType


@st.cache_resource
def get_driver():
    return webdriver.Chrome(
        service=Service(
            ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        ),
        options=options,
    )


options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--headless")
driver = get_driver()

conn = st.connection("Data", type=GSheetsConnection)
df_price = conn.read(
    spreadsheet="Copy of Port_op_Data",
    #spreadsheet="Port_op_Data",
    worksheet="Target"
    )

url = "https://www.settrade.com/th/research/iaa-consensus/main"
driver.get(url) #open website
xpath_filter = "/html/body/div[1]/div/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[3]"

optionbutton = "/html/body/div[1]/div/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[3]/div/div/ul/li[43]/button/div"
cookie_button = "/html/body/div[1]/div/div/div[7]/div/div/div[2]/button"
cookie = driver.find_element(By.XPATH, cookie_button)
cookie.click()
dropdown = driver.find_element(By.XPATH, xpath_filter)
#driver.execute_script("arguments[0].scrollIntoView();", dropdown)
dropdown.click()
option = driver.find_element(By.XPATH, optionbutton)
option.click()


time.sleep(5)

try:

    driver.execute_script("window.scrollBy(0, 1500);")
    time.sleep(5)
    #driver.execute_script("window.scrollBy(0, 1500);")
    #time.sleep(5)
except Exception as e:
    print(f"JavaScript error: {e}")

display_xpath = "/html/body/div[1]/div/div/div[2]/div[2]/div/div[3]/div/div[2]/div[1]/div[4]/div/div[1]/div/div[2]/div/div[1]"
display = driver.find_element(By.XPATH, display_xpath)
display.click()
time.sleep(1)
display50_xpath = "/html/body/div[1]/div/div/div[2]/div[2]/div/div[3]/div/div[2]/div[1]/div[4]/div/div[1]/div/div[2]/div/div[3]/ul/li[4]"
display50 = driver.find_element(By.XPATH, display50_xpath)
display50.click()


table_xpath = "/html/body/div[1]/div/div/div[2]/div[2]/div/div[3]/div/div[2]/div[1]/div[1]/div[2]/table"

# Locate the table
table = driver.find_element(By.XPATH, table_xpath)

# Extract table rows
rows = table.find_elements(By.TAG_NAME, "tr")

# Extract data from each row
table_data = []
for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    row_data = [cell.text for cell in cells]
    table_data.append(row_data)

if table_data[0] == []:
    table_data = table_data[1:]

tic_list = []
current_price_list = []
avg_price_list = []



driver.close()
# Print or save the data
for row in table_data:
    #print(row)
    tic_list.append(row[0])
    current_price_list.append(float(row[1]))
    avg_price_list.append(float(row[-1]))

iaa_dict = {'Ticker':tic_list, 'Price':current_price_list, 'Avg':avg_price_list}
iaa_df = pd.DataFrame(iaa_dict)
iaa_df['Upside'] = (iaa_df['Avg']/iaa_df['Price']) - 1 
iaa_df = iaa_df.sort_values(by=['Upside'], ascending=False)

iaa_df2 = iaa_df[['Ticker', 'Avg']][:25].copy()
#rename col to date
#iaa_df2.rename(columns=['Avg'])
st.dataframe(iaa_df2)