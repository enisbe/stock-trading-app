
from google.cloud import storage
import tensorflow as tf
from tensorflow import keras
from pypfopt import EfficientFrontier, objective_functions
from pypfopt import risk_models
from pypfopt import expected_returns  
import cvxpy as cp
import time
import pandas as pd
from datetime import datetime
from helper import stock_data_pull, fill_blanks, fill_blanks, pre_proc_df, predict, get_weights

from google.cloud import storage

"""
   Debuging TESTING THE PREDICTION FUNCTION
"""

# input window and forecast horizon
window = 60
horizon = 12
theta = window+horizon

sc = storage.Client()
recon_model = keras.models.load_model('gs://nbeats_stock_model/models_5_mins')

# read in stock ready data
stock_ready = pd.read_csv('stock_ready.csv')
stock_total = pd.read_csv('stock_total.csv')

dt_range = pd.date_range(start=stock_total.Datetime.max(),periods=horizon+1, freq='5min',closed='right')
predictions_df = predict(stock_ready,recon_model,window,horizon,dt_range)

predictions_df.to_csv('pred.csv',index=False)



