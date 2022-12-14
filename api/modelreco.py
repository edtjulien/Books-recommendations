import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

class BookReco:
    def __init__(self):
        self.data = None
        self.vectors = []
        self.scalars = []
        self.users_cs = None
        self.predict_scores = None
        self.weights = {}
        self.df_jaccard = None
        self.df_users = None
        self.data_empty = None
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

    def add_users(self, df_users, weight=1):
        self.weights = {**self.weights, 'users': weight}
        self.df_users = df_users

    def __get_cosine_similarity(self, prefix='sen_', data=None):
        if data is None:
            data_temp = self.data.filter(regex=f'^{prefix}',axis=1)
            data_temp = data_temp.fillna(0)
        else: data_temp = data
        vec = MinMaxScaler().fit_transform(data_temp)
        return cosine_similarity(vec)

    def fit(self, data):
        self.data = data
        self.data_empty = self.data[['book_id']]

        for i,vector in enumerate(self.vectors):
            feats_cs = self.__get_cosine_similarity(vector['col_name'])
            self.vectors[i] = {**vector, 'cosine_similar': feats_cs}

        for i,scalar in enumerate(self.scalars):
            X = self.data.loc[:,[scalar['col_name']]]
            X = MinMaxScaler().fit_transform(X)
            self.scalars[i] = {**scalar, 'scaled': X.reshape(-1)}

        if self.df_users is not None:
            self.users_cs = self.__get_cosine_similarity(prefix=None, data=self.df_users)

        del self.data # to reduce the size of the model. No need anymore the data

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

        if type(df1) is not pd.Series:
            return df2
        elif type(df2) is not pd.Series:
            return df1
        else:
            return pd.concat([df1,df2], axis=0)

    def predict(self, book_id):

        if self.data_empty is None:
            print(f"Fit the model before predict")
            return None
        
        try:
            index_book = self.data_empty.query('book_id == @book_id').index.values.astype(int)[0]
        except:
            print(f"Can't find book_id: {book_id} in the dataset")
            return None

        self.data_score = self.data_empty

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

        if self.users_cs is not None:
            score = self.users_cs[index_book]

            if score is not None:
                score = score * self.weights['users']
                weight_sum += self.weights['users']
                self.data_score = pd.concat([self.data_score, pd.Series(score, name='users')], axis=1)


        if weight_sum == 0:
            weight_sum == 1

        self.data_score =  self.data_score.sum(axis=1) / weight_sum

        #data = self.data.merge(pd.Series(self.data_score, name='score'), how='left', left_on='book_id', right_index=True)
        #return data.query('book_id != @book_id') # we pull off the asked book_id drom the scores
        return pd.Series(self.data_score[self.data_score.index != book_id], name='score')

    def format_predict(self, scores, max_books=5):
        scores = scores.sort_values(ascending=False)
        return scores[:max_books]

    def format_tojson(self, scores, data, max_books=5):
        data = data.copy().merge(scores, how='left', left_on='book_id', right_index=True)
        data = data.sort_values('score', ascending=False)

        output = []
        num = 0
        for _, book in data.iterrows():
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
