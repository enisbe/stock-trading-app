import json
import os

cloud_run = True
linux = True


# CONTAINER_URL = 'http://localhost:5051/'
CONTAINER_URL = 'https://db-ops-4453yfddza-uc.a.run.app/'
ROUTE_EXECUTION = 'target_execution'

if cloud_run:
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient() 
        
    PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER") 
    name_azure = f"projects/{PROJECT_NUMBER}/secrets/azure_secret/versions/latest"
    name_alpaca = f"projects/{PROJECT_NUMBER}/secrets/alpaca_secret/versions/latest"

    response_alpaca = client.access_secret_version(request={"name": name_alpaca})
    response_azure = client.access_secret_version(request={"name": name_azure})

    secret_alpaca  = json.loads(response_alpaca.payload.data) 
    secret_azure  = json.loads(response_azure.payload.data) 

    AZURE_CONNECTION_STRING =  secret_azure['AZURE_CONNECTION_STRING']
    KEY_ID = secret_alpaca['KEY_ID']
    SECRET_KEY = secret_alpaca['SECRET_KEY']
    BASE_URL = secret_alpaca['BASE_URL']

else: 
     
    with open("secrets.json", "r") as f:
        secrets =   json.load(f)

    if linux:        
        AZURE_CONNECTION_STRING =  secrets['AZURE_CONNECTION_STRING_LINUX2']
    else:
        AZURE_CONNECTION_STRING =  secrets['AZURE_CONNECTION_STRING_WINDOWS2']

    KEY_ID = secrets['KEY_ID']
    SECRET_KEY = secrets['SECRET_KEY']
    BASE_URL = secrets['BASE_URL']
    PROJECT_NUMBER = secrets['PROJECT_NUMBER']
