import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
from pytz import timezone
import config

 
def load_target(path):
    api = tradeapi.REST(config.KEY_ID, config.SECRET_KEY, config.BASE_URL)

    
    sys_df  = pd.read_csv(path)
    sys_df  = sys_df[['Ticker','Weight' ]]
    cash = 1- sys_df['Weight'].sum()
    cash_df = pd.DataFrame({'Ticker': 'CASH', "Weight": cash}, index=[0])
    
    df = pd.concat([sys_df,cash_df])
    tag = "None"
    file = path
    first = file.split("-")[0]
    if first=='target':
        tag = file.split("target-")[1].split('.')[0]
        tag = datetime.strptime(tag, '%Y%m%d-%H%M%S(EST)')
    return df, tag




def get_portfolio_value():
    
    api = tradeapi.REST(config.KEY_ID, config.SECRET_KEY, config.BASE_URL)
    account = api.get_account() 
    return float(account.portfolio_value)

# get_portfolio_value()


def get_prices(df):
    api = tradeapi.REST(config.KEY_ID, config.SECRET_KEY, config.BASE_URL)

    if "Price" not in df.columns.tolist():    
        df['Price'] = np.nan 

    df['Price']=np.nan
    for ticker in df.Ticker.tolist():
        if ticker=='CASH':
            continue
        latest_trade = api.get_latest_trade(ticker)
        df.loc[df['Ticker']==ticker,"Price"] = latest_trade.p 
    return df
 
def get_positions():
    
    api = tradeapi.REST(config.KEY_ID, config.SECRET_KEY, config.BASE_URL)
    positions = api.list_positions()
    if not positions:
        current_positions = pd.DataFrame(columns=['Ticker', 'Shares'])
    else:
        positions = pd.DataFrame([[position.symbol, int(position.qty)] for position in positions],columns =['Ticker',"Shares"])
    return positions


def execute_orders(target_execution):
    
    api = tradeapi.REST(config.KEY_ID, config.SECRET_KEY, config.BASE_URL)

    eastern = timezone('US/Eastern')
    ts = datetime.now(eastern)
    target_execution['timestamp'] = ts
    
    for order in target_execution.iterrows():
        order_dict = order[1].to_dict()
        order_submit = api.submit_order(
                        symbol=order_dict['Ticker'],
                        qty=order_dict['Trade Quantity'],   
                        side=order_dict['action'].lower(),
                        type='market',
                        time_in_force='day'                        
                        )
        print("|--Ticker: ", order_dict['Ticker'], "QTY: ", order_dict['Trade Quantity'],"Action: ",  order_dict['action'], "Status: ", order_submit.status)

    return target_execution

def is_trading_session():
    api = tradeapi.REST(config.KEY_ID, config.SECRET_KEY, config.BASE_URL)
    clock = api.get_clock()
    return clock.is_open


def rebalance(target_positions, current_positions, percent, portfolio_value=0,  tag = "None", debug = False):        
    
    if portfolio_value ==0:
        api = tradeapi.REST(config.KEY_ID, config.SECRET_KEY, config.BASE_URL)    
        portfolio_value = get_portfolio_value()
    
    
    system_dollars = percent/100. * portfolio_value
    
    merged = target_positions.merge(current_positions[['Ticker','Shares']], how='outer', on='Ticker')
    merged = merged.fillna(0)

    merged =  get_prices(merged)
    merged = merged[merged['Ticker'] != 'CASH']   

    merged['Value'] = merged['Price'] * merged['Shares']

    merged['targe_value']  = merged['Weight'] * system_dollars
    merged['targe_value'].fillna(0,inplace=True)
    merged['quantity'] = ((merged['targe_value']  - merged['Value']) /merged['Price']).astype('int')

    merged['action'] = merged['quantity'].apply(lambda x: "BUY" if x  >0 else 'SELL' )
    merged['quantity'] = np.abs(merged['quantity'])

    merged['action_type'] = merged.apply(lambda row:  "REBAL" if row['Value'] != 0 and row['targe_value'] !=0 else np.nan, axis=1)
    merged['action_type'] = merged.apply(lambda row: 'NEW' if row['Value'] == 0 else row['action_type'], axis=1)
    merged['action_type'] = merged.apply(lambda row: 'CLOSE' if row['targe_value'] == 0 else row['action_type'], axis=1)
    merged['New Shares'] = merged.apply(lambda x: x['Shares'] + x['quantity'] if x['action'] =='BUY' else x['Shares'] - x['quantity'], axis=1).astype(int)
    merged['New Value'] = merged['New Shares'] * merged['Price']
    merged = merged[['Ticker','Weight', 'Price', 'Value', "New Value", "Shares", 'quantity', 'action', 'New Shares', 'action_type' ]]
    merged.rename(columns = {'Value': "Value", 'Shares': "Current Shares", 'quantity': 'Trade Quantity'   }, inplace=True)
    merged = merged[merged['Trade Quantity'] > 0]
    merged['tag'] = tag
    return merged