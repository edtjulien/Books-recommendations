from fastapi import FastAPI
from model import BookReco

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
from sklearn.feature_extraction.text import CountVectorizer
import ast
import warnings
import json

# uvicorn api:app --reload

warnings.filterwarnings('ignore') 

df_books = pd.read_csv('../output/test.csv')

br = BookReco()
br.add_vector('tag_', weight=0)
br.add_vector('sen_', weight=10)
# br.add_scalar('book_rating_value', weight=5)
# br.add_scalar('book_nb_comm', weight=1)
br.fit(df_books)

app = FastAPI()

@app.get("/")
async def root(id):
    scores = br.predict(int(id))

    res = br.format_prediction(scores, max_books=5)
    print(res)
    if res is None:
        return {"message": 'Nothing'}
    else: return {"message": str(res)}