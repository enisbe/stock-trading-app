# Rebalance and Execute trades Cloud Functions

The function can be deployed from a local gcloud SDK environment or via a google cloud shell. The following environment variable must be set first:
```
gcloud config set project $PROEJECT_ID

export PROJECT_NUMBER=$(gcloud projects list --filter="$(gcloud config get-value project)" --format="value(PROJECT_NUMBER)")
export DB_KEY=[KEY]
export GCS_BUCKET=[BUCKET WHERE FILE IS DROPPED] 
export CREDENTIALS=[CREDITIAL FILE]
export SAVE_BUCKET=[WHERE TO SAVE FAILED/SUCCESS JOBS]
export ENVIROMENT=[ENVIROMENT]
```

Once the variables are set we can deploy it via gcloud command:

```
gcloud functions deploy executioner_test --entry-point main --runtime python37  --set-env-vars PROJECT_NUMBER=$PROJECT_NUMBER  --set-env-vars DB_KEY=$DB_KEY  --set-env-vars CREDENTIALS=$CREDENTIALS --set-env-vars SAVE_BUCKET=$SAVE_BUCKET --set-env-vars ENVIROMENT=$ENVIROMENT --set-env-vars GCS_BUCKET=$GCS_BUCKET --trigger-resource $GCS_BUCKET --trigger-event google.storage.object.finalize

``` 

This function uses cloud secrets to manage credentials to the database. However, permission must be set for cloud functions to have access to cloud secrets:
 
* In Security-> Secrets Manager  add principal to `<project_id>@appspot.gserviceaccount.com`. The added role should be `Secrets Manager Accessor`
* Same should be done Cloud Run - account `<project_id>-compute@developer.gserviceaccount.com` Role `Secrets Manager Accessor`
