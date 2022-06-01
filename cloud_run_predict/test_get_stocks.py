
import os
from os import listdir
from os.path import isfile, join
from google.cloud import storage

import tensorflow as tf
from tensorflow import keras

from pypfopt import EfficientFrontier, objective_functions
from pypfopt import risk_models
from pypfopt import expected_returns  
import cvxpy as cp

import pytz

import time
import pandas as pd
from datetime import datetime
from helper import stock_data_pull, fill_blanks, fill_blanks, pre_proc_df, predict, get_weights
"""
    Un flasking the main.py app
"""
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'cloud_storage_service_key.json'

#model_bucket_name = 'nbeats_stock_model/models_5_mins'

# load model
sc = storage.Client()
recon_model = keras.models.load_model('gs://nbeats_stock_model/models_5_mins')

# input window and forecast horizon
window = 60
horizon = 12
theta = window+horizon


# functions to pre-process input date
stock_total = stock_data_pull()
stock_ready = pre_proc_df(stock_total)   

stock_total.to_csv('stock_total.csv',index=False)

stock_ready.to_csv('stock_ready.csv',index=False)
