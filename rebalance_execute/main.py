import pandas as pd
import rebal
import importlib as imp
import os
import json
import config
import requests

BASE_URL = config.CONTAINER_URL
ROUTE_ACTIVITIES = config.ROUTE_ACTIVITIES
ROUTE_ACCOUNT = config.ROUTE_ACCOUNT
ROUTE_EXECUTION = config.ROUTE_EXECUTION



def write_execution_2db(target_execution, custom_tag):
    
    
    db_key = os.environ.get("DB_KEY")
    #Create JSON payload
    df_payload = target_execution.to_dict()
    json_payload = {}
    json_payload['DB_KEY'] = db_key
    json_payload['df'] = df_payload
    json_payload['custom_tag'] =custom_tag
    json_payload = json.dumps(json_payload,default=str)

    # What if write fail? How to we recover? Save to disk and retry later?
    r = requests.post(f"{BASE_URL}{ROUTE_EXECUTION}", json=json_payload)
    print(f"|--Write execution DB") 
    response = json.loads(r.text)
    print("Message:", response['response'], "Code:",  response['code'])    
    
    r = requests.get(f"{BASE_URL}{ROUTE_ACCOUNT}?db_key={db_key}")
    print(f"|--Write account snapshot to DB") 
    response = json.loads(r.text)
    print("Message:", response['response'], "Code:", response['code']) 

def rebalance_and_execute(target_file):
    print("\t|--Create Rebalance from Target.")
    target_positions, tag  = rebal.load_target(target_file) #  target_positions
    current_positions = rebal.get_positions() 
    target_execution = rebal.rebalance(target_positions, current_positions, 95, rebal.get_portfolio_value(), tag = tag)
    
  
    print("\t|--Execute.")
    target_execution = rebal.execute_orders(target_execution)
    
    print("\t|--Write to Database.")
    write_execution_2db(target_execution, "Development")



def main(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    file = event
    f = file['name']
    f = f.split("/")
    f = f[len(f)-1]
    f = f.split('-')
    
    if not rebal.is_trading_session():
        print("|--Market Closed")
        # return 
    else:
        print("|--Market Open")

     
    first = f[0]
    if first=='target':
        print(f"|--Trigger file found: {file['name']}.")
        # rebalance_and_execute(file['name'])
        
        print("|--Execution complete")
#         
    else:
        print(f"Not Target File : {file['name']}.")

# file = {}
# file['name'] ='target-20220506-133000(EST).csv'

# main(file, "context")