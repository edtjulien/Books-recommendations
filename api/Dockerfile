#FROM continuumio/miniconda3
FROM python:3.10-slim-bullseye

WORKDIR /home/app

RUN apt-get update
# install nano and unzip
RUN apt-get install nano unzip
# used to build programs from source code
RUN apt install build-essential -y

# copy requirements.txt in the container and install dependencies with pip
RUN pip install fastapi scikit-learn pandas numpy dill uvicorn

# run the mlflow server in the container
# CMD mlflow server -p $PORT \
#     --host 0.0.0.0 \
#     --backend-store-uri $BACKEND_STORE_URI \
#     --default-artifact-root $ARTIFACT_ROOT

CMD uvicorn api:app --reload --host 0.0.0.0 --port $API_PORT