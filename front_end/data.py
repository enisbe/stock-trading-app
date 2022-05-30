import numpy as np
import pandas as pd

def get_trades(df):
    # df_nvda = df[df['symbol']=='NVDA'].sort_values(by=['timestamp', 'symbol'])
    df_ = df.sort_values(by=['symbol', 'timestamp'])
    df_['side_sign'] = np.where(df_['side'] =="sell", 1,-1)
    df_['qty_sign'] = np.where(df_['side'] =="sell", 1*df_['qty'],-1*df_['qty'])
    df_['cash'] = df_['side_sign'] * df_['qty'] * df_['price']
    df_['cum_qty'] = df_.groupby('symbol') ['qty_sign'].cumsum()
    df_['closed'] =  np.where(df_['cum_qty']==0,'CLOSED',None)
    df_['closed_count'] =  np.where(df_['cum_qty']==0,1,0)
    df_['closed'] = df_ .groupby("symbol")['closed'].transform(lambda x: x.fillna(method ='bfill' ))  #   fillna( method ='bfill', inplace=True)
    df_['closed_count']  = df_ .groupby("symbol")['closed_count'].transform(lambda x: x.fillna(method ='bfill'))  #   fillna( method ='bfill', inplace=True)
    df_['trade_window'] =  df_.loc[::-1, 'closed_count'].cumsum()[::-1]
    df_close = df_[df_['closed']=='CLOSED']
    df_open =  df_[df_['closed']!='CLOSED']
    return df_close, df_open


def process_closed(df):
    df['timestamp'] = df['timestamp'].dt.tz_convert("US/Eastern") # .max()  - df_nvda['timestamp'].dt.tz_convert("US/Eastern").min() 
    df['timestamp_min'] = df.groupby(['symbol', 'trade_window'])['timestamp'].transform('min') 
    df['timestamp_max'] = df.groupby(['symbol', 'trade_window'])['timestamp'].transform('max')
    df['minutes_held'] = (df['timestamp_max']  - df['timestamp_min']).apply(lambda x: x.total_seconds()/60)
    df['invested'] = df.groupby(['symbol', 'trade_window'])['cash'].transform(lambda x: np.abs(x[(x<0)].sum()))

    trades = pd.pivot_table( 
        df, 
        # margins=True,
        # columns =['timestamp' , 'cash' ],
        values=[  'timestamp_min', 'timestamp_max' ,'invested', 'cash', 'minutes_held'], 
        index=['symbol', 'trade_window'], 
        aggfunc = { 
                    'timestamp_min': lambda x: str(x.min().strftime("%Y-%m-%d %H:%M:%S")),
                    'timestamp_max':  lambda x: str(x.max().strftime("%Y-%m-%d %H:%M:%S")),
                    'invested': 'mean',
                    'cash': lambda x: x.sum(), 
                    'minutes_held': lambda x: x.min()
                  }
        )


    trades = trades.reset_index()
    trades['return'] = trades['cash']/trades['invested']
    trades = trades.rename(columns={'timestamp_min': 'Open Date', 'timestamp_max':
                                    "Closed Date", 'symbol': "Symbol", 
                                    "trade_window": "Trade Number", "cash": "Profit $" , 
                                    "invested": "Invested $", 'minutes_held': 
                                    "Holding (min)" , "return": "Return %"})
    trades = trades[['Open Date', 'Closed Date', "Trade Number" , "Symbol",  "Invested $", "Profit $", "Holding (min)", "Return %"]]
    return trades

def arrow(x):     
    formater ='↓ {:.2%}'.format(x) if x < 0  else '↑ {:.2%}'.format(x)
    return formater   

def format_closed_df(df):
     return df.style.format({"Return %": arrow, 
                             'Invested $':'${:,.0f}'.format ,
                             'Profit $':'{:,.0f}'.format, 
                             'Holding (min)':'{:,.0f}'.format}, 
                             subset=['Return %',  'Invested $', 'Profit $', 'Holding (min)']) \
                            .applymap(lambda x: f"color: {'darkred' if x <0  else 'darkgreen'}", subset=['Return %']) \
                            .bar(subset=['Profit $'], color= ['#d65f5f', '#5fba7d'], width=80, align='zero')

