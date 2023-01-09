import warnings

import dill
import modelreco
import numpy as np
import pandas as pd
from config import DEFAULT_MODEL_PARAMS
from fastapi import FastAPI
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_distances, cosine_similarity
from sklearn.preprocessing import MinMaxScaler, StandardScaler

# uvicorn api:app --reload
# uvicorn api:app --reload --host 0.0.0.0 --port 8000

warnings.filterwarnings("ignore")

with open("../output/final/model-reco.obj", "rb") as f:
    br = dill.load(f)

app = FastAPI()


@app.get("/")
async def root(id):
    br.set_weight(DEFAULT_MODEL_PARAMS)

    scores = br.predict(int(id))
    res = br.format_tojson(scores, max_books=5)

    if res is None:
        return {"message": "Nothing"}
    else:
        return {"message": res}
