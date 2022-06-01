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

import os
from os import listdir
from os.path import isfile, join

import pytz


est_tz = pytz.timezone("US/Eastern")
tag=datetime.now(est_tz).strftime('%Y%m%d-%H%M%S(EST)_testmodel')

predictions_df = pd.read_csv('pred.csv')

new_weights = get_weights(predictions_df)

tgt_actn_file = f"target_{tag}.csv"
new_weights.save_weights_to_file(tgt_actn_file) # save locally

weights_df = pd.read_csv(tgt_actn_file)
weights_df.columns = ['Ticker','Weight']
weights_df_slim = weights_df[weights_df.Weight != 0 ]

filepath = os.path.join(tgt_actn_file)
os.remove(filepath)   

weights_df_slim.to_csv(tgt_actn_file,index=False)