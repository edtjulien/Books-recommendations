# %%
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
from sklearn.feature_extraction.text import CountVectorizer
import ast
import warnings

warnings.filterwarnings('ignore') 

from sklearn.preprocessing import StandardScaler, MinMaxScaler

class BookReco:
    def __init__(self):
        self.data = None
        self.vectors = []
        self.scalars = []
        self.predict_scores = None

    def add_vector(self, col_prefix, weight=1):
        self.vectors.append({'col_name': col_prefix, 'weight': weight})

    def add_scalar(self, col_name, weight=1):
        self.scalars.append({'col_name': col_name, 'weight': weight})

    def __get_cosine_similarity(self, prefix):
        data_temp = self.data.filter(regex=f'^{prefix}',axis=1)
        data_temp = data_temp.fillna(0)
        vec = MinMaxScaler().fit_transform(data_temp)
        return cosine_similarity(vec)

    def fit(self, data):
        self.data = data

        for i,vector in enumerate(self.vectors):
            feats_cs = self.__get_cosine_similarity(vector['col_name'])
            self.vectors[i] = {**vector, 'cosine_similar': feats_cs}

        for i,scalar in enumerate(self.scalars):
            X = self.data.loc[:,[scalar['col_name']]]
            X = MinMaxScaler().fit_transform(X)
            self.scalars[i] = {**scalar, 'scaled': X.reshape(-1)}

    def predict(self, book_id):
        scores = []

        try:
            index_book = self.data.query('book_id == @book_id').index.values.astype(int)[0]
        except:
            print(f"Can't find book_id: {book_id} in the dataset")
            return None
        
        # get all scores, apply weight
        for vector in self.vectors:
            score = vector['cosine_similar'][index_book]
            scores.append(score*vector['weight'])
        
        for scalar in self.scalars:
            scores.append(scalar['scaled']*scalar['weight'])

        # sum of all scores
        self.predict_scores = None
        for score in scores:
            if self.predict_scores is None:
                self.predict_scores = np.array(score)
            else: self.predict_scores += np.array(score)

        # normalisation of sum of all scores
        self.predict_scores = MinMaxScaler().fit_transform(self.predict_scores.reshape(-1,1))
        return self.predict_scores

    def format_prediction(self, scores, max_books):
        scores = [(i,bi) for i,bi in enumerate(scores)]
        sorted_scores = sorted(scores, key=lambda x:x[1], reverse=True)
        sorted_scores = sorted_scores[1:max_books+1]
        return [(i, self.data.iloc[i,:]['book_id'],self.data.iloc[i,:]['title'],s) for i,s in sorted_scores]



# %%
# %%


# %%



