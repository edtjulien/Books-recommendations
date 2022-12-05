from fastapi import FastAPI

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
from sklearn.feature_extraction.text import CountVectorizer
import warnings
import dill
import modelreco

from sklearn.preprocessing import StandardScaler, MinMaxScaler

# uvicorn api:app --reload
# uvicorn api:app --reload --host 0.0.0.0 --port 8000

warnings.filterwarnings('ignore') 

with open('model-reco.obj', 'rb') as f:
    br = dill.load(f)

app = FastAPI()

@app.get("/")
async def root(id):
    br.set_weight({'tag_': 0, 'sen_': 10, 'jaccard': 10, 'book_rating_value': 2, 'book_nb_comm': 0, 'book_rating_count': 0})

    scores = br.predict(int(id))
    res = br.format_tojson(scores, max_books=5)

    if res is None:
        return {"message": 'Nothing'}
    else: return {"message": res}