# Rebalance and Execute trades Cloud Functions

```
gcloud config set project container-deploy


export PROJECT_NUMBER=$(gcloud projects list --filter="$(gcloud config get-value project)" --format="value(PROJECT_NUMBER)")
export DB_KEY=[KEY]

export GCS_BUCKET=[BUCKET]
gcloud functions deploy executioner --entry-point main --runtime python37  --set-env-vars PROJECT_NUMBER=$PROJECT_NUMBER  --set-env-vars DB_KEY=$DB_KEY  --trigger-resource $GCS_BUCKET --trigger-event google.storage.object.finalize
```