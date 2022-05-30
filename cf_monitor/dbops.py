import sqlalchemy
from datetime import datetime, timedelta
from pytz import timezone
import alpaca_trade_api as tradeapi
import pyodbc
import urllib
import config
import pandas as pd

create_db_sql ="""
drop table if exists activities;
 
CREATE   TABLE activities(
                id varchar(200) PRIMARY KEY, 
                order_id varchar(200),  
                timestamp  datetimeoffset ,   
                symbol  varchar(10),    
                side varchar(10),
                price NUMERIC(18,2),
                qty NUMERIC,
                leaves_qty NUMERIC,
                cum_qty NUMERIC,
                order_status VARCHAR(20),
                type VARCHAR(20)                
);
 
drop table if exists recommendations;
CREATE TABLE recommendations(      
                ticker varchar(10),
                price NUMERIC (18,2),    
                weight NUMERIC (18,2),
                old_value NUMERIC (18,2),
                new_value NUMERIC (18,2),
                old_shares NUMERIC,
                trade_quantity NUMERIC,
                new_shares NUMERIC,
                action varchar(10),
                action_type varchar(10),
                target_tag varchar(50),
                execution_timestamp  datetimeoffset,
                custom_tag varchar(50),
                order_id varchar(100),
                PRIMARY KEY (ticker, target_tag)
            );
drop table if exists account_summary;
           
            
CREATE TABLE account_summary(
                timestamp datetimeoffset PRIMARY KEY,
                account_number varchar(50),
                shorting_enabled varchar(10),
                portfolio_value   NUMERIC (18,2),
                long_market_value NUMERIC (18,2),
                cash NUMERIC (18,2),
                buying_power NUMERIC (18,2)
                );

DROP TABLE stock_trading.dbo.history;

CREATE TABLE stock_trading.dbo.history (
	[timestamp] datetimeoffset PRIMARY KEY,
    timeframe varchar (20), 
	portoflio_value float,
	profit_loss float,
	profit_loss_pct float
	
);
   

"""
 


def create_insert_with_id_constraints(table, fields, id_field):

    if not isinstance(id_field, list):
        id_field = [id_field]
    else:
        id_field = id_field
    table = table
    
    col_str = ",".join(fields)
    fmt = ['\'{}\''] *len(fields)
    val_str = ",".join(fmt)
    val_str
    
    where_id_clause = " and ".join([f"source.{f}=v.{f}" for f in id_field])
    
    insert_statement = """
    INSERT {} ({})
    SELECT {}
        FROM (VALUES ({})) v ({})
        WHERE NOT EXISTS (SELECT 1
                          FROM {} as source 
                          WHERE {}  
                         );
    """.format(table, col_str, col_str, val_str, col_str, table, where_id_clause)     
    return insert_statement

 

fields = ['ticker', 'price', 'weight', 'old_value', 'new_value', 'old_shares', 
          'trade_quantity', 'new_shares', 'action', 'action_type', 'target_tag', 'custom_tag', 
          'order_submited_at', 'order_id','status']
table_name ="recommendations"
primary_keys = ['ticker', 'order_id']

insert_execution = create_insert_with_id_constraints(table_name,fields,primary_keys)
    
def create_db():
    with pyodbc.connect(config.AZURE_CONNECTION_STRING) as cnxn:
        con = cnxn.cursor()
        con.execute(create_db_sql)
        con.commit()

        
        
def write_target_execution_2db(df):
    
    with pyodbc.connect(config.AZURE_CONNECTION_STRING) as cnxn:

        con = cnxn.cursor()
        
        for rec in df.iterrows():
            row = rec[1]        
            sql =  insert_execution.format( row.Ticker,
                                            row.Price,
                                            row.Weight,
                                            row['Value'],
                                            row['New Value'],
                                            row['Current Shares'],
                                            row['Trade Quantity'],
                                            row['New Shares'],
                                            row['action'],                             
                                            row.action_type,
                                            row.tag,
                                            row.custom_tag,
                                            row.order_submited_at,
                                            row.order_id, 
                                            row.status)
            con.execute(sql)        
            con.commit()

fields = ['timestamp', 'account_number', 'shorting_enabled', 'portfolio_value', 'long_market_value', 'cash', 'buying_power']
table_name ="account_summary"
primary_keys = ['timestamp']

insert_account = create_insert_with_id_constraints(table_name,fields,primary_keys)
    


def update_account():
     
    api = tradeapi.REST(config.KEY_ID, config.SECRET_KEY, config.BASE_URL)

    with pyodbc.connect(config.AZURE_CONNECTION_STRING) as cnxn:

        con = cnxn.cursor()
    
        eastern = timezone('US/Eastern')
        account_snap = api.get_account()
        
        ts = datetime.now(eastern)
        sql =  insert_account.format(ts,
                                    account_snap.account_number,
                                    account_snap.shorting_enabled, 
                                    account_snap.portfolio_value, 
                                    account_snap.long_market_value,
                                    account_snap.cash, 
                                    account_snap.buying_power)

        con.execute(sql)
        con.commit()
 
    

fields = ['id', 'order_id', 'timestamp', 'symbol', 'side', 'price', 'qty', 'leaves_qty', 'cum_qty', 'order_status', 'type']
table_name ="activities"
primary_keys = ['id']

insert_activity = create_insert_with_id_constraints(table_name,fields,primary_keys)
    



def write_activity_2db(days=0):

    api = tradeapi.REST(config.KEY_ID, config.SECRET_KEY, config.BASE_URL)
  
    with pyodbc.connect(config.AZURE_CONNECTION_STRING) as cnxn:

        con = cnxn.cursor()
        
        for day in range(0,days):
            td = timedelta(days=day)
            download_date = str(datetime.today().date()- td)

            activities = api.get_activities(date=download_date)
            print(f"Total Activities for {download_date} date:", len(activities))
            for activity in activities:  
                sql =  insert_activity.format(activity.id,
                                                activity.order_id,
                                                activity.transaction_time,
                                                activity.symbol,
                                                activity.side,
                                                activity.price,
                                                activity.qty,
                                                activity.leaves_qty,
                                                activity.cum_qty,
                                                activity.order_status,activity.type)
                # print(sql)
                con.execute(sql)
                con.commit()
        
        
    
fields = ['timestamp', 'timeframe', 'portoflio_value', 'profit_loss', 'profit_loss_pct']
table_name ="history"
primary_keys = ['timestamp']

insert_history = create_insert_with_id_constraints(table_name,fields,primary_keys)
    

def write_history(timeframe='15Min', days=0):

    df = get_history(timeframe=timeframe, days=days)
   
    with pyodbc.connect(config.AZURE_CONNECTION_STRING) as cnxn:

        con = cnxn.cursor()
        for rec in df.iterrows():
            row = rec[1]
            sql =  insert_history.format(row['timestamp'],
                                         row['timeframe'],
                                         row.portoflio_value,
                                         row.profit_loss,
                                         row.profit_loss_pct
            )
            con.execute(sql)
            con.commit()
                    

                    
def get_history(timeframe ='15Min', days=0):
    
    api = tradeapi.REST(config.KEY_ID, config.SECRET_KEY, config.BASE_URL)
    
    from datetime import datetime, timedelta
    download_start = str(datetime.today().date()- timedelta(days=days))
    download_end = str(datetime.today().date()- timedelta(days=0))
    history = api.get_portfolio_history(date_start=download_start,
                                        date_end = download_end, 
                                        timeframe='1D')
    df = pd.DataFrame({'timestamp':  history.timestamp, 
                       'timeframe': ['1D'] * len( history.timestamp),
                       "portoflio_value": history.equity, 
                       "profit_loss": history.profit_loss, 
                       "profit_loss_pct": history.profit_loss_pct})
    df [['timestamp']]= df[['timestamp']].apply(lambda x: pd.to_datetime(x, utc=True,  unit='s').dt.tz_convert("US/Eastern"))
    return df