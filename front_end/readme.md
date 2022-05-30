
# Deploy front end as a streamlit container

This contaier is build locally and push to the cloud contaier repository.

Step 1: Build container and test locally

```
docker build -t front_end:v1.0 .
export MYPORT=9092 # any port is fine
docker run --rm --name front_end -p 8600:${MYPORT} -e PORT=${MYPORT} front_end:v1.0
docker container kill front_end
```


Step 2: Deploy to cloud. Use glcoud SDK locally installed

``` bash
$ gcloud config set project  capstone-498-group
$ gcloud config set compute/region us-central1
$ gcloud config set compute/zone us-central1-b
$ gcloud services enable run.googleapis.com containerregistry.googleapis.com
$ gcloud auth configure-docker
$ docker tag front_end:v1.0  gcr.io/capstone-498-group/front_end:v1.0
$ docker push gcr.io/capstone-498-group/front_end:v1.0
```

Step 3: Once container is push execute either locally or in cloud shell deployment command


```
export PROJECT_NUMBER=$(gcloud projects list --filter="$(gcloud config get-value project)" --format="value(PROJECT_NUMBER)")
export PROJECT_ID=[project id]



gcloud run deploy frontend --image gcr.io/$PROJECT_ID/front_end:v1.0 --platform managed --set-env-vars PROJECT_NUMBER=$PROJECT_NUMBER   --allow-unauthenticated --max-instances=1 --region us-central1 --memory 2Gi --timeout=900
```