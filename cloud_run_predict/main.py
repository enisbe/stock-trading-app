from flask import Flask, render_template, request

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


# load model
sc = storage.Client()
recon_model = keras.models.load_model('gs://nbeats_stock_model/models_5_mins')

# input window and forecast horizon
window = 60
horizon = 12
theta = window+horizon

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

text = 'success !'

@app.route("/")
def index():
    # functions to pre-process input date
    stock_total = stock_data_pull()
    stock_ready = pre_proc_df(stock_total)    

    # create dates for forecast horizon
    dt_range = pd.date_range(start=stock_total.Datetime.max(),periods=horizon+1, freq='5min',closed='right')
    #date_label = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
    est_tz = pytz.timezone("US/Eastern")
    tag=datetime.now(est_tz).strftime('%Y%m%d-%H%M%S(EST)_prod_model')

    predictions_df = predict(stock_ready,recon_model,window,horizon,dt_range)

    storage_client_ex = storage.Client.from_service_account_json(
        'capstone-498-group-storage-admin.json'
    )
    #bucket = storage_client_ex.get_bucket('stock-trading-app-drop-bucket')
    bucket = storage_client_ex.get_bucket('stock-trading-app-drop-bucket-prod') # changed to prod

    # prediction file
    pred_file = f"predictions_{tag}.csv"
    predictions_df.to_csv(pred_file,index=False)

    # send to Enis's Bucket  # don't send for the time being
    with open(pred_file, 'rb') as my_file:
        bucket.blob(pred_file).upload_from_file(my_file)

    # get target weights
    new_weights = get_weights(predictions_df)

    tgt_actn_file = f"target_{tag}.csv"
    new_weights.save_weights_to_file(tgt_actn_file) # save locally

    weights_df = pd.read_csv(tgt_actn_file)
    weights_df.columns = ['Ticker','Weight']
    weights_df_slim = weights_df[weights_df.Weight != 0 ]

    filepath = os.path.join(tgt_actn_file)
    os.remove(filepath)   

    weights_df_slim.to_csv(tgt_actn_file,index=False)

    with open(tgt_actn_file, 'rb') as my_file:
        bucket.blob(tgt_actn_file).upload_from_file(my_file)

    # remove local files

    filepath = os.path.join(pred_file)
    os.remove(filepath)   

    filepath = os.path.join(tgt_actn_file)
    os.remove(filepath)   
    return render_template('index.html', html_page_text=text)

print('success!')

if __name__ == "__main__":
    app.run(debug=False, port=int(os.environ.get("PORT", 8080)))
