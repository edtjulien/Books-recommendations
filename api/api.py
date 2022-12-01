from fastapi import FastAPI

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
from sklearn.feature_extraction.text import CountVectorizer
import ast
import warnings
import json
import pickle
import dill
import marshal
from model import BookReco

from sklearn.preprocessing import StandardScaler, MinMaxScaler

# uvicorn api:app --reload

warnings.filterwarnings('ignore') 


df = pd.read_json('../output/final/data-books.json', lines=True)

br = BookReco()
br.add_vector('tag_', weight=2)
br.add_vector('sen_', weight=10)
br.add_scalar('book_rating_value', weight=0)
br.add_scalar('book_nb_comm', weight=0)
br.fit(df)

# with open('../recommendation/data/model-reco.obj', 'rb') as f:
#     model = dill.load(f)

app = FastAPI()

@app.get("/")
async def root(id):

    scores = br.predict(int(id))
    res = br.format_tojson(scores, max_books=5)

    if res is None:
        return {"message": 'Nothing'}
    else: return {"message": res}