import requests
import config
import os
import json
import alpaca_trade_api as tradeapi

db_key = os.environ.get("DB_KEY")

def is_trading_session():
    api = tradeapi.REST(config.KEY_ID, config.SECRET_KEY, config.BASE_URL)
    clock = api.get_clock()
    return clock.is_open



def main(data, context):  

    if not is_trading_session():
        print("|--Market Closed")
        # return

    try:
        print("|--Updating Account")
        r = requests.get(f"{config.CONTAINER_URL}{config.ROUTE_ACCOUNT}?db_key={db_key}")
        print(f"|--Write account snapshot to DB") 
        response = json.loads(r.text)
        print("Message:", response['response'], "Code:", response['code']) 

    except Exception as e:
        print(e)     


main("data", "context")