import requests
import config
import os
import json

db_key = os.environ.get("DB_KEY")
 
def main(data, context):  

    try:
        print("|--Updating Activities")
        r = requests.get(f"{config.CONTAINER_URL}{config.ROUTE_ACTIVITIES}?db_key={db_key}&days=1")
        print(f"|--Write activities to DB") 
        response = json.loads(r.text)
        print("Message:", response['response'], "Code:", response['code']) 

    except Exception as e:
        print(e)     


main("data", "context")