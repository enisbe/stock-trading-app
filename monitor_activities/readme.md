
# Deploy Google Cloud Function

```
gcloud config set project [PROJECT_ID]
export PROJECT_NUMBER=$(gcloud projects list --filter="$(gcloud config get-value project)" --format="value(PROJECT_NUMBER)")

export DB_KEY=[key]
gcloud functions deploy activites  --entry-point main --runtime python37 --set-env-vars PROJECT_NUMBER=$PROJECT_NUMBER  --set-env-vars DB_KEY=$DB_KEY  --trigger-resource daily_topic --trigger-event google.pubsub.topic.publish --timeout 540s
```

Note: Must enable secrets by add role to

```container-deploy@appspot.gserviceaccount.com with role of Secret Manager Secret Accessor```