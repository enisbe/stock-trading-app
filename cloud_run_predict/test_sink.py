from google.cloud import storage

storage_client = storage.Client.from_service_account_json(
    'capstone-498-group-storage-admin.json'
)
#bucket = storage_client.get_bucket('stock-trading-app-drop-bucket')
bucket = storage_client.get_bucket('stock-trading-app-drop-bucket-prod') # changed to prod

for item in list(bucket.list_blobs()):
    print(item)