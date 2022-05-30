from flask import Flask, request, jsonify, render_template
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import logging
from flask.logging import create_logger
import pickle
import pandas as pd
import json 
import os

import dbops 

app = Flask(__name__)
LOG = create_logger(app)
LOG.setLevel(logging.INFO)

key  = os.environ.get("DB_KEY")


@app.route('/update_account',methods=['GET'])
def update_account():
    """Takes the account snapshot (balance,equity etc)"""
    
    LOG.info("|--Update Account Called")    
    LOG.info("\t|--Updating Accounts")   

    try: 
        passed_key = request.args.get('db_key',default="1", type=str)
        print(passed_key)
        if passed_key != key:
            return {
                    "code": '401',
                    "response": "access denied"
                }
        
        
        dbops.update_account()
        return {
            "code": '200',
            "response": "update_account success"
        }
    
    except Exception as e:
        LOG.info(e)
        return {
            "code": '400',
            "response": str(e)
        }  

@app.route('/activities',methods=['POST','GET'])
def update_activities():
    """
    Updates activities table based on the amount
    of data specified in the query parameter
    """
    
    LOG.info("|--Update Activities Called")    
    LOG.info("\t|--Updating Activity")

    try: 
        passed_key = request.args.get('db_key',default="1", type=str)
        if passed_key != key:
            return {
                    "code": '401',
                    "response": "access denied"
                }

        days = request.args.get('days',default=1, type=int)
        days = max(min(days,7),1)
        LOG.info(f"\t|--Dowloading activites for {days} days")


        dbops.write_activity_2db(days=days)

        return {
        "code": '200',
        "response": "update_activities success"
        }
    
    except Exception as e:
        return {
            "code": '400',
            "response": str(e)
        }  
 
 


@app.route('/target_execution', methods=['POST'])
def target_execution():
    """
    Target recommendations table. Updates the recommendations 
    when the rebalance files is executation. Current all executation 
    are update which might create some overhead.
    """
    
    LOG.info("|--Function Called")    
    LOG.info("\t|--Updating Activity")
    
    try:
        
        json_payload =   request.json         
        process_json = json.loads(json_payload)
        passed_key =  process_json.get('DB_KEY')
        df = process_json.get('df')
        custom_tag = process_json.get('custom_tag')
        
        target_execution = pd.DataFrame(df)
        
    except Exception as e:
        return {
                "code": '400',
                "response": f"error reading JSON payload {e}" 
               }

    try:
        
        if passed_key != key:
            return {
                    "code": '401',
                    "response": "access denied"
                }
 
        dbops.write_target_execution_2db(target_execution)
    
        return {
                "code": '200',
                "response": "update_execution success"
            }
    except Exception as e:
        return {
            "code": '400',
            "response": print(str(e))
        }  


    

@app.route('/history', methods=['GET'])
def history():
    """ Target History table to update performance history"""
    
    LOG.info("|--Function Called")    
    LOG.info("\t|--Updating History")
    
    try: 
        passed_key = request.args.get('db_key',default="1", type=str)
        if passed_key != key:
            return {
                    "code": '401',
                    "response": "access denied"
                }
        
        timeframe = request.args.get('timeframe',default='15Min', type=str)
        days = request.args.get('days',default=1, type=int)
        days = max(min(days,7),1)
        LOG.info(f"\t|--Dowloading history for {days} days")


        dbops.write_history(timeframe=timeframe, days=days)

        return {
        "code": '200',
        "response": "update_activities success"
        }
    
    except Exception as e:
        return {
            "code": '400',
            "response": str(e)
        }  
    
    
if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in Dockerfile
   
    # app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT")))   
    app.run(debug=True, host='0.0.0.0', port=5051)   