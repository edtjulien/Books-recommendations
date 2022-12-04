import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

class BookReco:
    def __init__(self):
        self.data = None
        self.vectors = []
        self.scalars = []
        self.predict_scores = None
        self.weights = {}
        self.df_jaccard = None
        self.data_score = None

    def add_vector(self, col_prefix, weight=1):
        self.weights = {**self.weights, col_prefix: weight}
        self.vectors.append({'col_name': col_prefix})

    def add_jaccard(self, df, weight=1):
        self.weights = {**self.weights, 'jaccard': weight}
        self.df_jaccard = df

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

    def set_weight(self, weights:dict):
        self.weights = weights

    def __get_jaccard_score(self, book_id):
        df_jaccard = self.df_jaccard.copy()
        df_jaccard = df_jaccard.rename(columns = {'Unnamed: 0':'book_id'})
        df_jaccard = df_jaccard.set_index('book_id')

        try:
            df1 = df_jaccard.query('book_id == @book_id').transpose().dropna().squeeze()
            df2 = df_jaccard.loc[:, str(book_id)].dropna()
        except:
            print('Error Jaccard in __get_jaccard_score')
            return None

        return pd.concat([df1,df2], axis=0)

    def predict(self, book_id):

        try:
            index_book = self.data.query('book_id == @book_id').index.values.astype(int)[0]
        except:
            print(f"Can't find book_id: {book_id} in the dataset")
            return None
        
        # init data_score to empty
        self.data_score = self.data[['book_id']]

        # get all scores, apply weight
        weight_sum = 0 # to normalize at the end, like a mean
        for vector in self.vectors:
            score = vector['cosine_similar'][index_book]
            weight = self.weights[vector['col_name']]
            weight_sum += weight

            self.data_score = pd.concat([self.data_score, pd.Series(score*weight, name=vector['col_name'])], axis=1)
        
        for scalar in self.scalars:
            weight = self.weights[scalar['col_name']]
            weight_sum += weight
            self.data_score = pd.concat([self.data_score, pd.Series(scalar['scaled']*weight, name=scalar['col_name'])], axis=1)

        self.data_score = self.data_score.set_index('book_id')

        
        if self.df_jaccard is not None:
            score = self.__get_jaccard_score(book_id) 

            if score is not None:
                score = score * self.weights['jaccard']
                weight_sum += self.weights['jaccard']
                self.data_score = self.data_score.merge(pd.Series(score, name='jaccard'), how='left', left_index=True, right_index=True)

        if weight_sum == 0:
            weight_sum == 1

        self.data_score =  self.data_score.sum(axis=1) / weight_sum

        data = self.data.merge(pd.Series(self.data_score, name='score'), how='left', left_on='book_id', right_index=True)

        return data.query('book_id != @book_id') # we pull off the asked book_id drom the scores

    def format_tojson(self, scores, max_books):

        output = []
        num = 0

        scores = scores.sort_values('score', ascending=False)

        for _, book in scores.iterrows():
            output.append({
                'title' : book['title'],
                'url' : book['book_url'],
                'image' : book['img_url'],
                'author' : book['surname']+' '+book['name'],
                'author_url' : book['book_author_url'],
                'book_rating_value' : book['book_rating_value'],
                'book_rating_count' : book['book_rating_count'],
                'score' : str(book['score']),
            })
            if num == max_books - 1:
                break
            num += 1
        return output
