import sqlite3
import warnings

import dill
import modelreco
import numpy as np
import pandas as pd
from config import DB_FILE, DEFAULT_MODEL_PARAMS, MAX_TO_PREDICT, MODEL_FILE
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_distances, cosine_similarity
from sklearn.preprocessing import MinMaxScaler, StandardScaler

# uvicorn api:app --reload
# uvicorn api:app --reload --host 0.0.0.0 --port 8000

warnings.filterwarnings("ignore")

with open(MODEL_FILE, "rb") as f:
    model = dill.load(f)

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_data_byid(table, book_id, books_id_list=None):
    conn = sqlite3.connect(DB_FILE)
    if books_id_list is not None:
        sql_query = pd.read_sql(
            f'SELECT * FROM {table} WHERE book_id IN ({ ",".join(books_id_list) })',
            conn,
        )
    else:
        sql_query = pd.read_sql(
            f'SELECT * FROM {table} WHERE book_id="{book_id}"', conn
        )
    conn.close()
    return pd.DataFrame(sql_query)


@app.get("/")
async def root(id):
    model.set_weight(DEFAULT_MODEL_PARAMS)
    scores = model.predict(int(id))
    books_id_list = [str(bid) for bid in list(scores.index)]
    df_books_reco = get_data_byid("books", None, books_id_list=books_id_list)
    res = model.format_tojson(scores, df_books_reco, max_books=MAX_TO_PREDICT)

    if res is None:
        return {"message": "Nothing"}
    else:
        return {"message": res}
