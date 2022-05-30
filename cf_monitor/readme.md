# Deploy monitor container

You must declare environmental variables first:

```
export PROJECT_NUMBER=$(gcloud projects list --filter="$(gcloud config get-value project)" --format="value(PROJECT_NUMBER)")
export DB_KEY=[keyhere]
```
Note DB_KEY is any random set of the character set by the user at deployment. Currently, the application exposes IP to anyone on the internet. To prevent anyone from making a db request DB_KEY specified at the deployment must match DB_KEY in the `get request` signature. This is just to add some security and prevent anyone on the internet from making random DB requests. This is a high-level security measure and if greater security is needed it must be implemented separately. 

Deploy application command:

```
gcloud run deploy db-ops --set-env-vars PROJECT_NUMBER=$PROJECT_NUMBER  --set-env-vars DB_KEY=$DB_KEY --platform managed --allow-unauthenticated --region us-central1 --source  . 
```
TODO: 

* Add gcloud CLI commands for cloud scheduler to that run periodically

