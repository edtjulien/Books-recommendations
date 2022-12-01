# %%
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
from sklearn.feature_extraction.text import CountVectorizer
import ast
import warnings

warnings.filterwarnings('ignore') 

from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.preprocessing import StandardScaler, MinMaxScaler

class BookReco:
    def __init__(self):
        self.data = None
        self.vectors = []
        self.scalars = []
        self.predict_scores = None
        self.weights = {}

    def add_vector(self, col_prefix, weight=1):
        self.weights = {**self.weights, col_prefix: weight}
        self.vectors.append({'col_name': col_prefix})

    def add_scalar(self, col_name, weight=1):
        self.weights = {**self.weights, col_name: weight}
        self.scalars.append({'col_name': col_name})

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

    # def __get_cosine_similarity_final(self,scores):
    #     X = [list(score) for score in scores]
    #     X = MinMaxScaler().fit_transform(X)
    #     cs = cosine_similarity(np.array(X).T)
    #     return MinMaxScaler().fit_transform(cs)

    def set_weight(self, weights:dict):
        self.weights = weights

    def predict(self, book_id):
        scores = []

        try:
            index_book = self.data.query('book_id == @book_id').index.values.astype(int)[0]
        except:
            print(f"Can't find book_id: {book_id} in the dataset")
            return None
        
        # get all scores, apply weight
        weight_sum = 0 # to normalize at the end, like a mean
        for vector in self.vectors:
            score = vector['cosine_similar'][index_book]
            weight = self.weights[vector['col_name']]
            weight_sum += weight
            scores.append(score*weight)
        
        for scalar in self.scalars:
            weight = self.weights[vector['col_name']]
            weight_sum += weight
            scores.append(scalar['scaled']*weight)

        # sum of all scores
        self.predict_scores = None

        for score in scores:
            if self.predict_scores is None:
                self.predict_scores = np.array(score)
            else: self.predict_scores += np.array(score)
        
        # todo : mettre scores dans un dataframe des scores avec une Serie avec index book_id + faire l'ordre inverse, selection des n premier et minmaxscaler (bof la fin)

        # normalisation of sum of all scores
        #return MinMaxScaler().fit_transform(self.predict_scores.reshape(-1,1))
        return self.predict_scores / weight_sum

    def format_prediction(self, scores, max_books):
        scores = [(i,bi) for i,bi in enumerate(scores)]
        sorted_scores = sorted(scores, key=lambda x:x[1], reverse=True)
        sorted_scores = sorted_scores[1:max_books+1]
        return [(i, self.data.iloc[i,:]['book_id'],self.data.iloc[i,:]['title'],s) for i,s in sorted_scores]
    
    def format_tojson(self, scores, max_books):

        scores = [(i,bi) for i,bi in enumerate(scores)]
        sorted_scores = sorted(scores, key=lambda x:x[1], reverse=True)
        sorted_scores = sorted_scores[1:max_books+1]

        output = []
        num = 0
        for i,s in sorted_scores:
            book = self.data.iloc[i,:]
            output.append({
                'title' : book['title'],
                'url' : book['book_url'],
                'image' : book['img_url'],
                'author' : book['surname']+' '+book['name'],
                'author_url' : book['book_author_url'],
                'score' : str(s),
            })
            if num == max_books:
                break
            num += 1
        return output
