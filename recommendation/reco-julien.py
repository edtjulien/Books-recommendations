# %%
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
from sklearn.feature_extraction.text import CountVectorizer
import ast
import warnings
import dill

warnings.filterwarnings('ignore') 

pd.set_option("display.max_columns", 100) # ‘None’ value means unlimited.

THEMES = {
 'amitie': 373,
 'amour': 77,
 'autobiographie': 45,
 'aventure': 33,
 'bande-dessinee': 18,
 'biographie': 31,
 'cinema': 89,
 'classique': 28,
 'comedie-romantique': 3788,
 'comics': 142,
 'drogue': 863,
 'dystopie': 879,
 'emotion': 4100,
 'enquetes': 3988,
 'entretiens': 708,
 'essai': 13,
 'famille': 290,
 'fantastique': 7,
 'fantasy': 4,
 'geographie': 187,
 'guerre': 91,
 'humour': 15,
 'humour-noir': 621,
 'jeunesse': 14,
 'journalisme': 975,
 'litterature-americaine': 9,
 'litterature-asiatique': 1064,
 'litterature-francaise': 3,
 'manga': 12,
 'musique': 44,
 'nouvelles': 23,
 'peur': 430,
 'poesie': 25,
 'politique': 54,
 'psychologie': 65,
 'racisme': 906,
 'recit-de-voyage': 448,
 'religion': 26,
 'reportage': 3488,
 'reseaux-sociaux': 26109,
 'roman': 1,
 'roman-fantastique': 912,
 'roman-noir': 136,
 'romans-policiers-et-polars': 63883,
 'science-fiction': 6,
 'sentiments': 1770,
 'serie': 788,
 'theatre': 21,
 'thriller': 11,
 'thriller-psychologique': 1073,
 'tragedie': 601,
 'western': 533
}



# %% [markdown]
# # Merging files and datasets

# %%
def merge_data_files(books_file_list:list, books_meta_file=None, books_senti_file=None, books_users_file=None):
    df_books = None

    # fusion of mains books data files with comments
    for filename in books_file_list:
        df_books_temp = pd.read_json(filename, lines=True)
        if df_books is None:
            df_books = df_books_temp
        else: df_books = pd.concat([df_books, df_books_temp])

    df_books = df_books.drop(['tags'],axis=1)

    # genre du profil per user_id
    if books_users_file is not None:
        df_users = pd.read_json(books_users_file, lines=True)
        df_books = df_books.merge(df_users, on='user_id', how='left')
    df_books = df_books.fillna('')

    # join to the meta data books file
    if books_meta_file is not None:
        df_meta = pd.read_json(books_meta_file, lines=True)
        df_meta = df_meta.drop(['book_nb_comm', 'title', 'name', 'surname','img_url','book_date'],axis=1)
        df_books = df_books.merge(df_meta, on='book_id', how='inner')

    # join sentiments file
    if books_senti_file is not None:
        df_senti = pd.read_json(books_senti_file, lines=True)
        df_senti = df_senti.drop(['title'],axis=1)
        df_books = df_books.merge(df_senti, on='book_id', how='left')
    df_books = df_books.fillna(0)

    return df_books

# %%
df_comm = merge_data_files(
    books_file_list = ['../output/books-julien.json','../output/books-rebecca.json'],
    books_meta_file = '../output/books-meta-data.json',
    books_senti_file = '../output/vecteurs_sentiments.json',
    books_users_file = '../output/users-data.json'
    )

# %%
# df_comm['year'] = df_comm['book_date'].str.extract(r'\b(\d{4})\b').replace('1900','').replace('3889',)
# df_comm['year'].unique()

# %%
df_comm

# %%
# group by per book
columns_senti = [col for col in df_comm.columns if col.startswith('sen_')]
columns_book = ['book_id', 'book_url', 'book_nb_comm', 'title', 'name', 'surname',
       'tags', 'img_url', 'book_rating_count', 'book_rating_value',
       'book_author_url', 'book_editor', 'book_pages', *columns_senti]

def reduce_comm_to_books(df):
    return df.copy().groupby(columns_book, as_index=False).count().loc[:,columns_book]

# %%
df_books = reduce_comm_to_books(df_comm)

# %% [markdown]
# We have now 2 dataset : df_comm and df_books with 2 differents aggregate levels

# %% [markdown]
# # Preprocessing df_books

# %%
# on garde que les tags avec le nom dans filter_list ou si la valeur est supérieur à filter_force_min. ca permet de rétirer les tags rares et peu importants
def tags_to_cols(df, col_name, filter_list=None, filter_force_min=24):
    df1 = df.copy()

    for index,row in df.iterrows():
        tags_as_string = row[col_name]
        tags = ast.literal_eval(tags_as_string)

        for tag in tags:
            if filter_list is not None and not tag[0].strip() in filter_list and tag[1] < filter_force_min:
                continue
            tag_name = 'tag_'+tag[0].strip().replace(' ','_').lower()
            df1.loc[df1.index == index, tag_name] = tag[1]

    df1 = df1.fillna(0)
    return df1

# %%
df_books = tags_to_cols(df_books, col_name='tags', filter_list=list(THEMES.keys()), filter_force_min=24)

# %%
df_books.to_json('../output/final/data-books.json',lines=True,orient='records')
df_comm.to_json('../output/final/data-comm.json',lines=True,orient='records')

# %% [markdown]
# # Simple Model

# %%
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


# %%
br = BookReco()
br.add_vector('tag_', weight=2)
br.add_vector('sen_', weight=10)
br.add_scalar('book_rating_value', weight=0)
br.add_scalar('book_nb_comm', weight=0)
br.fit(df_books)

# %%
scores = br.predict(1829) # De Cape et de Crocs, tome 2 : Pavillon noir !
br.set_weight({'tag_': 0.5, 'sen_': 10, 'book_rating_value': 0, 'book_nb_comm': 0})
br.format_tojson(scores, max_books=5)

# %%
import pickle
import dill


with open('data/model-reco.obj', "wb") as f:
    dill.dump(br, f)

# with open('data/model-reco.obj', 'wb') as f:
#     pickle.dump(br, f, pickle.HIGHEST_PROTOCOL)

# %%



