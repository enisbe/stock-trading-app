# Deploy
```
export PROJECT_NUMBER=$(gcloud projects list --filter="$(gcloud config get-value project)" --format="value(PROJECT_NUMBER)")
export DB_KEY=[keyhere]
gcloud run deploy db-ops --set-env-vars PROJECT_NUMBER=$PROJECT_NUMBER  --set-env-vars DB_KEY=$DB_KEY --platform managed --allow-unauthenticated --region us-central1 --source  . 
```

Speed up builds. Build up to the requirements and then just build the last piece
* https://cloud.google.com/build/docs/speeding-up-builds#:~:text=Unlike%20%2D%2Dcache%2Dfrom%20%2C%20which,builder%20supported%20by%20Cloud%20Build.
 