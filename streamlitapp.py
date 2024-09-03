# streamlit_app.py

import streamlit as st
from streamlit_gsheets import GSheetsConnection
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta



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


def check_TRI_price():
    #driver = get_driver()
    url = 'https://www.set.or.th/en/market/index/tri/overview'
    driver.get(url)

    #SET50 TRI
    index_xpath = '/html/body/div[1]/div/div/div[2]/div/div[2]/div[2]/div/div/div/div/div[2]/div[2]/table/tbody/tr[2]/td[2]'
    index = driver.find_element(By.XPATH, index_xpath)
    update = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[2]/div[2]/div/div/div/div/div[1]/span')

    index_float = float(index.text.replace(",",""))

    TRI = {'index':index_float, 'update':update.text[6:]}
    #driver.quit()
    return TRI

def check_SET50_price():
    #driver = get_driver()
    url = 'https://www.set.or.th/en/market/index/set50/overview'
    driver.get(url)

    index_xpath = '/html/body/div[1]/div/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]'
    update_xpath = '/html/body/div[1]/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div[2]/span'
    index = driver.find_element(By.XPATH, index_xpath)
    index_update = driver.find_element(By.XPATH, update_xpath)

    index_float = float(index.text.replace(",",""))

    SET50 = {'index':index_float, 'update': index_update.text}

    #driver.quit()

    return SET50

def dl_set50(SET50_data):
    TRI = check_TRI_price()
    SET50 = check_SET50_price()
    check_TRI_date = datetime.strptime(TRI['update'], '%d %b %Y')
    check_data_date = datetime.strptime(SET50_data.index[-1], '%d/%m/%Y')

    if check_TRI_date > check_data_date:
        df_tri = pd.DataFrame({'SET50':[SET50['index']], 'SET50_TRI':[TRI['index']]}, index = [check_TRI_date.strftime("%d/%m/%Y")])
        df_tri.index.name = 'DATE'
        df_tri2 = pd.concat([SET50_data,df_tri])
    else:
        st.write('data is up to date')
    return df_tri2

def del_time(df_to_del):
    date_str = []
    for datee in list(df_to_del.index):
    # Convert to Pandas datetime object
        date_time_obj = pd.to_datetime(datee)

        # Remove time from the datetime object
        date_var = date_time_obj.date()

        # Convert the date object to a string
        date_str.append(date_var.strftime('%Y-%m-%d'))

    df_to_del.index = date_str
    return df_to_del

def download_pricedata(old_price_data):
    old_price_data = del_time(old_price_data)
    tic_list = old_price_data.columns.to_list()
    SET_MAI = []
    for ticker in tic_list:
        SET_MAI.append(ticker + ".BK")
    #get lastest date
    lastest_date = old_price_data.index[-1]
    lastest_date = datetime.strptime(lastest_date, '%Y-%m-%d')+ timedelta(days = 1)
    lastest_date = lastest_date.strftime('%Y-%m-%d')
    present_date = datetime.today().strftime('%Y-%m-%d')
    #download lastest to present date
    price_data2 = yf.download(SET_MAI, start=lastest_date, end=present_date )['Close']
    price_data2.columns = [col[:-3] for col in price_data2.columns]
    #combine
    price_data4 = del_time(old_price_data)
    price_data5 = del_time(price_data2)
    price_data3 = pd.concat([price_data4, price_data5])
    #price_data3 = price_data3.drop_duplicates(subset='Date')
    price_data3.index.name = 'Date'

    return price_data3

def download_new_ticker(new_ticker_file,price_data):
    not_in_list = []
    new_ticker = new_ticker_file['Symbol'].to_list()
    old_ticker = price_data.columns.to_list()
    for ticker in new_ticker:
        if ticker not in old_ticker:
            not_in_list.append(ticker)

    if not_in_list != []:
        first_date = price_data.index[0]
        lastest_date = price_data.index[-1]
        dl_price = yf.download(not_in_list, start=first_date, end=lastest_date )['Close']
        if len(not_in_list) == 1:
            dl_df = dl_price.to_frame(name = not_in_list[0])
        else:
            dl_df = dl_price
        
        combine_price_data = pd.concat([price_data, dl_df], axis = 1)
    else:
        combine_price_data = price_data

    return combine_price_data
def download_all(price_df, tri_df):

    try:
        df_tri = dl_set50(tri_df)
    except:
        st.warning("please reboot")
        st.stop

    if isinstance(df_tri, pd.DataFrame):
        new_price_data = download_pricedata(price_df)
        st.dataframe(df_tri)
        st.dataframe(new_price_data)    
    return {'Price':new_price_data, 'TRI': df_tri}


def select_option(option, tri_df, price_df, ticker_list):
    if option == 'Price':
        df = download_pricedata(price_df)
        name = 'SET_MAI_Close.csv'
    elif option == 'TRI':
        try:
            df = dl_set50(tri_df)
            name = 'SET50TRI_Close.csv'
        except:
            st.warning("please reboot")
    elif option == 'add new ticker to price':
        df = download_new_ticker(ticker_list,price_df)
        name = 'SET_MAI_Close.csv'
    csv = convert_df(df)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name=name,
        mime="text/csv",
    )

    return df


options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--headless")
driver = get_driver()

conn = st.connection("Price", type=GSheetsConnection)
df_price = conn.read(worksheet="SET_MAI_Close")
df_price = df_price.set_index('Date')
price_date = df_price.index[-1]
compare_price = datetime.strptime(price_date, '%Y-%m-%d')
price_date = compare_price.strftime('%d/%m/%Y')

df_TRI = conn.read(worksheet="Benchmark")
df_TRI = df_TRI.set_index('DATE')
TRI_date = df_TRI.index[-1]

compare_TRI = datetime.strptime(TRI_date, '%d/%m/%Y')



todaydate = datetime.today()


#show last updated date
st.write(f"Last Price Date {price_date}")
st.write(f"Last TRI Date {TRI_date}")




#button download new price/ data 
#daily donwload
st.subheader("Daily download")


#trouble shooting
#conn_test = st.connection("test", type=GSheetsConnection)
#df_test = conn_test.read()
#st.dataframe(df_test)
#new = ['6/5/2024', 3, 0]
#df_test.loc[len(df_test)] = new
#st.dataframe(df_test)
#if st.button("Update worksheet"):
#    df = conn_test.update(
#        data=df_test,
#    )

#separate download



#update list



if "Button1" not in st.session_state:
    st.session_state["Button1"] = False

if "Button2" not in st.session_state:
    st.session_state["Button2"] = False

if st.button("Button1"):
    st.session_state["Button1"] = not st.session_state["Button1"]
    new_TRI = dl_set50(df_TRI)

    new_price = download_pricedata(df_price)


    st.dataframe(new_price.tail())

    new_price = new_price.reset_index()
    st.session_state['price'] = new_price
    new_TRI = new_TRI.reset_index()
    st.session_state['TRI'] = new_TRI

    st.dataframe(st.session_state['price'].tail())
    st.dataframe(st.session_state['TRI'].tail())
if st.session_state["Button1"]:
    if st.button("Button2"):
        st.session_state["Button2"] = not st.session_state["Button2"]
        #conn_price.update(data = new_price)
        conn.update(worksheet = "SET_MAI_Close", data =st.session_state['price'])
        conn.update(worksheet = "Benchmark", data =st.session_state['TRI'])
        st.toast('update complete')
        st.success('update complete')
        #del st.session_state['TRI']

        
st.write(
    f"""
    ## Session state:
    {st.session_state["Button1"]=}

    {st.session_state["Button2"]=}
    """
)