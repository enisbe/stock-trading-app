import yfinance as yf
import requests
import pandas as pd

import tensorflow as tf
from tensorflow import keras

from pypfopt import EfficientFrontier, objective_functions
from pypfopt import risk_models
from pypfopt import expected_returns  
import cvxpy as cp

payload=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
# grab all tickers and put them into a list

basket = payload[0]['Symbol'].tolist()

# used for testing only!
#basket = ['AMZN', 'CTXS', 'DPZ', 'EBAY', 'EFX', 'FE', 'FFIV', 'FLT', 'FTNT', 'HAS']

def stock_data_pull():
  """
  Download Stock data
  """
  stock_final = pd.DataFrame()
  # iterate over each symbol
  for i in basket:  
      
      # print the symbol which is being downloaded
      print( str(basket.index(i)) + str(' : ') + i, sep=',', end=',', flush=True)  
      
      try:
          # download the stock price 
          stock = []
          #stock = yf.download(i,period = "2y",interval='5m', progress=False)
          # for intraday yahoo finance only let's you pull past 60 days. 
          # however there is only a 1 month option
          stock = yf.download(i,period = "1d",interval='5m', progress=False) ## pull only 1 day of information

          # append the individual stock prices 
          if len(stock) == 0:
              None
          else:
              stock['Name']=i
              stock_final = stock_final.append(stock,sort=False)
      except Exception:
          None
  return stock_final

def fill_blanks(df,srl_num,range,value_variable,date_variable):
  """
  fills missing observations
  some stocks may not have the same number of observations
  """
  stage_df = df.copy()
  for comb in stage_df[srl_num].unique(): 
    temp = stage_df[stage_df[srl_num] == comb].copy()
    stage_df = stage_df[stage_df[srl_num] != comb] # remove existing series detail
    temp2 = range.merge(temp,how='left',on=date_variable)
    # since we are filling missing data, other fields will be missing to
    # value info will be filled by zero, for other fields, we simply forward fill
    # Then back fill for full missing value coverage    
    #temp2[value_variable].fillna(0,inplace=True)
    temp2.fillna(method='ffill',inplace=True)
    temp2.fillna(method='bfill',inplace=True)
    # replace with new, full data subset
    stage_df = stage_df.append(temp2,ignore_index=True)
  return stage_df

def pre_proc_df(stock_total):
  stock_total.reset_index(inplace=True)
  stock_total = stock_total[['Datetime','Close','Name']]

  # homogenous the samples in each stock
  date_range = stock_total.Datetime.drop_duplicates()
  date_range = pd.DataFrame(date_range)

  stock_ready = fill_blanks(stock_total,'Name',date_range,'Close','Datetime')
  stock_ready.sort_values(by=['Name','Datetime'],inplace=True)
  return stock_ready

def predict(df,input_model,window,horizon,dt_range):
    pred_list = []
    for i, tckr in enumerate(df.Name.unique()):
        temp = df[df.Name == tckr].iloc[:window,:].copy()

        x_temp = temp.Close.values
        print(x_temp.shape)
        #test = x_test_temp.reshape(1,x_test_temp.shape[0],1)
        x_input = x_temp.reshape(1,window)
        pred = input_model.predict(x_input)

        for i in range(horizon):
            pred_list.append({'stock':tckr,'Datetime':dt_range[i],'Forecasted_Close':pred[0][i]})

    pred_df = pd.DataFrame(pred_list)
    #pred_df['Datetime'] = pd.to_datetime(pred_df['Datetime']).dt.date
    return pred_df

def get_weights(df):
    pivoted = df.pivot(index='Datetime', columns="stock", values="Forecasted_Close")
    mu = expected_returns.capm_return(pivoted, frequency=len(pivoted.index))
    mu1 = mu.sort_values(ascending=False).head(100)  # 
    df_S=pivoted[[x for x in mu1.index]]
    S = risk_models.sample_cov(df_S,frequency=len(pivoted.index))

    # Optimize for maximal Sharpe ratio
    ef = EfficientFrontier(mu1, S)
    ef.add_constraint(lambda w: w[0]+w[1]+w[2]+w[3]+w[4]+w[5]+w[6]+w[7]
                    +w[8]+w[9]+w[10]+w[11]+w[12]+w[13]
                    +w[14]+w[15]+w[16]+w[17]+w[18]+w[19]
                    == int(1))
    ef.add_constraint((lambda w: cp.sum(w) == 1))

    raw_weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights(rounding=3)

    return ef    