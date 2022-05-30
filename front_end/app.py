import pandas as pd
import streamlit as st
import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
 
import sys
from google.cloud import storage as cs_storage
import pytz


import sqlalchemy
from datetime import datetime, timedelta
# from pytz import timezone
import alpaca_trade_api as tradeapi
import urllib
import pandas as pd
import numpy as np

import data


import config
import alpaca_trade_api as tradeapi
import yfinance as yf


def get_history(benchmark):
    api = tradeapi.REST(config.KEY_ID, config.SECRET_KEY, config.BASE_URL)
    port = api.get_portfolio_history(timeframe='1D').df
    port.reset_index(inplace=True)
    port['Date'] = port['timestamp'].apply(lambda x: x.date())
    port['Date'] = pd.to_datetime(port['Date']) # ['profit_loss_pct']
   
    data = yf.download(benchmark, start="2020-01-01", end=str(datetime.today().date()++ timedelta(days=1)), progress=False) 

    data.reset_index(inplace=True)
    # port  = port[["Date",'equity']].merge(data[["Date","Adj Close"]] , on='Date')
    port_comb = port[["Date",'equity']].merge(data[["Date","Adj Close"]] , on='Date' , how='left')
    port_comb.columns = ['Date', "Account",benchmark]
    port_comb.set_index("Date",inplace=True)
    return port_comb.ffill()

string = config.AZURE_CONNECTION_STRING
params = urllib.parse.quote_plus(string)
conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
engine = sqlalchemy.create_engine(conn_str) 


st.set_page_config(
    page_title="Trading System Assessment",
    layout="wide")
 
st.markdown("""
           # Trading System Portfolio Assessment             
            """)
st.sidebar.header("Parametars")
raw = st.sidebar.checkbox('View Last 10 trades')

 


@st.cache 
def get_data():
    df = pd.read_sql("activities",engine)
    return df
df = pd.read_sql("activities",engine)



closed_trades , open_trades = data.get_trades(df)



processed_closed = data.process_closed(closed_trades)
processed_closed.drop('Open Date' ,axis=1,inplace=True)
# processed_closed.rename(columns={"Trade Number": "Trade#", "Holding Period (min)": "H. Period(min)"},inplace=True) #  ('Open Date',axis=1,inplace=True)

processed_closed.rename(columns={"Trade Number": "Trade#"},inplace=True) #  ('Open Date',axis=1,inplace=True)

bench = st.sidebar.selectbox(
    "Benchmark",
    ['QQQ', 'SPY'] 
)

port_comb  = get_history(bench)
port_comb.index = pd.Series(port_comb.index).dt.date 
 

date = st.sidebar.selectbox(
    'View after date:',
     pd.Series(port_comb.index),
    index = 8
)


port_comb = port_comb[port_comb.index>=date]

 


import plotly.express as px 

hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """

cumprod =  (port_comb.pct_change(1).fillna(0)+1).cumprod()

port_comb  = port_comb.reset_index()
cumprod = cumprod.reset_index()
fig = px.line(cumprod, x='Date', y=[bench, 'Account'], width=600, height=400)

fig.update_layout(title_text=f"Portfolio vs {bench}", title_x=0.5)

col =  st.columns(4)

c1 = col[0]
with c1:
    st.plotly_chart(fig)


# c2.plotly_chart(fig)

portfolio_return = cumprod.iloc[cumprod.shape[0]-1]['Account']
index_return = cumprod.iloc[cumprod.shape[0]-1][bench]

portfolio_values = port_comb.iloc[port_comb.shape[0]-1] ['Account']
index_values = port_comb.iloc[port_comb.shape[0]-1][bench]
as_of_date =  port_comb.iloc[port_comb.shape[0]-1]['Date']

dollar_change_account = port_comb.diff(1).iloc[port_comb.shape[0]-1]['Account']
dollar_change_index  = port_comb.diff(1).iloc[port_comb.shape[0]-1][bench]
pct_daily_change_account = port_comb.drop('Date',axis=1).pct_change(1).iloc[port_comb.shape[0]-1]['Account']
pct_daily_change_index = port_comb.drop('Date',axis=1).pct_change(1).iloc[port_comb.shape[0]-1][bench]




c2 = col[1]
with c2:
    st.write(" ")
  
c3 = col[2]

with c3:
    st.markdown(f"### Total Return:")
    st.write(f"Date: {as_of_date}")
    st.metric(f"Account ", f"{portfolio_values:,.0f}", f"{  portfolio_return -1 :.1%}"  )
    # st.markdown("### Index")
    st.metric(f"{bench}", f"{index_values:.2f}", f"{  index_return -1 :.1%}" )

c4 = col[3]


with c4:
    st.markdown(f"### 1 Day Change:")
    st.write(f"Today: {as_of_date}")
    st.metric(f"Account ", f"{dollar_change_account:,.0f}", f"{  pct_daily_change_account   :.1%}"  )
    # st.markdown("### Index")
    st.metric(f"{bench}", f"{dollar_change_index:.2f}", f"{  pct_daily_change_index   :.1%}" )



col_num = 2
cols = st.columns(col_num)

c = cols[0]

c.header("Top 10 Closed Trades")
c.markdown(hide_table_row_index, unsafe_allow_html=True)
c.dataframe(data.format_closed_df(processed_closed.sort_values(by="Profit $", ascending=False).head(10)) ,height=400 )


c = cols[1]
c.header("Bottom 10  Closed  Trades")
c.markdown(hide_table_row_index, unsafe_allow_html=True)
c.dataframe(data.format_closed_df (processed_closed.sort_values(by="Profit $", ascending=True).head(10)),  height=400)



if raw:
    sql = """
    SELECT top 10 [timestamp], symbol, side, price, qty, order_status 
    FROM stock_trading.dbo.activities
    order by [timestamp] DESC ;
    """
    df = pd.read_sql(sql,engine)
    df['timestamp'] = pd.to_datetime(df.timestamp).dt.tz_convert("US/Eastern").apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
    st.header("Last 10 Trades")

    st.dataframe(df, height=500)
