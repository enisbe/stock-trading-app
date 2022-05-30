import pandas as pd
import rebal
import importlib as imp
import os
import json
import config
import requests
from google.cloud import storage as gs_storage
from datetime import datetime


ENV = os.environ.get("ENVIROMENT")
CREDENTIALS_FILE  = os.environ.get("CREDENTIALS")
SAVE_BUCKET = os.environ.get("SAVE_BUCKET")
cloud = True


BASE_URL = config.CONTAINER_URL
ROUTE_EXECUTION = config.ROUTE_EXECUTION




storage_client = gs_storage.Client.from_service_account_json(
    CREDENTIALS_FILE
)
bucket = storage_client.get_bucket(SAVE_BUCKET)


def save_data(df, success):
    """
    Backup data helper function
    """

    print("Success: ", success)
    save_name = f"execution_{str(df.tag.iloc[0])}_{df.custom_tag.iloc[0]}_{str(datetime.now())}"

    if cloud: 
        if success:
            bucket.blob(f"success/{save_name}.csv").upload_from_string(df.to_csv(index=False), 'text/csv')
        else:
            bucket.blob(f"failure/{save_name}.csv").upload_from_string(df.to_csv(index=False), 'text/csv')
    else:
        if success:
            df.to_csv(f"success/{save_name}.csv", index=False)
        else:
            df.to_csv(f"failure/{save_name}.csv", index=False)

        
        
def write_execution_2db(target_execution):    
    
    """
    This functions ensure that we save and back up the data to db.
    In case the write fails (Timeout or something else), then write
    to respective folders (success/failure)
    """

    # Executions are written to db via cloud run container.

    db_key = os.environ.get("DB_KEY") 
    df_payload = target_execution.to_dict()
    json_payload = {}
    json_payload['DB_KEY'] = db_key
    json_payload['df'] = df_payload

    json_payload = json.dumps(json_payload,default=str)
    try:
        # What if write fail? How do we recover? Save to disk and retry later?
         
        r = requests.post(f"{BASE_URL}{ROUTE_EXECUTION}", json=json_payload)
        print(f"|--Write execution DB") 
        print(r.text)
        response = json.loads(r.text)
        print("Message:", response['response'], "Code:",  response['code'])

        # if the response is not 200 then we write  the execution file
        # to failure/ folder else we write to success/ folder

        if response['code']=='200':
            save_data(target_execution, success=True)
        else:
            save_data(target_execution, success=False)

    except Exception as e:

        # if for some reason we are unable to pass json payload 
        # we write to failure/ folder.

        save_data(target_execution, success=False)
        print("From Cloud Function write Execution:", str(e)) 

def rebalance_and_execute(target_file):
    """
    Create rebalance actions
    """
    print("\t|--Create Rebalance from Target.")
    target_positions, tag, custom_tag  = rebal.load_target(target_file) 
    current_positions = rebal.get_positions() 
    target_execution = rebal.rebalance(target_positions, current_positions, 95, 
                                        rebal.get_portfolio_value(), tag = tag, 
                                        custom_tag = custom_tag)
   
    # Execute
    print("\t|--Execute.")
    target_execution = rebal.execute_orders(target_execution)
 
    # Finally write the execution to database
    print("\t|--Write to Database.")
    write_execution_2db(target_execution)



def main(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    
    # We pick up the file name and search the first term in the file name

    file = event
    f = file['name']
    f = f.split("/")
    f = f[len(f)-1]
    f = f.split('_')
   

    # Only execute if market is open and if in production
    # ignore if testing
    if not rebal.is_trading_session():
        print("|--Market Closed")
        if ENV=="PROD": # do not execute if its in prod
             return 
    else:
        print("|--Market Open")

     
    first = f[0]
    # if first term is target that we have the target file to execute
    if first=='target':
        print(f"|--Trigger file found: {file['name']}.")
        rebalance_and_execute(file['name'])        
        print("|--Execution complete")
        # Do I need to drop the table?
    else:
        print(f"Not Target File : {file['name']}.")
        
        
 