# Google Cloud Function to request account updates

```
 
gcloud config set project [PROJECT_ID]
 export PROJECT_NUMBER=$(gcloud projects list --filter="$(gcloud config get-value project)" --format="value(PROJECT_NUMBER)")

export DB_KEY=[KEY]
gcloud functions deploy monitor  --entry-point main --runtime python37 --set-env-vars PROJECT_NUMBER=$PROJECT_NUMBER  --set-env-vars DB_KEY=$DB_KEY  --trigger-resource daily_topic --trigger-event google.pubsub.topic.publish --timeout 540s
```

Must enable secrets by adding role to

```container-deploy@appspot.gserviceaccount.com  Secret Manager Secret Accessor```