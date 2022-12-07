import pandas as pd
import plotly.express as px

dict_mapping = {'janvier' : 'January',
                'février' : 'February',
                'fevrier' : 'February',
                'mars' : 'March',
                'avril' : 'April',
                'mai' : 'May',
                'juin' : 'June',
                'juillet': 'July',
                'août' : 'August',
                'septembre' : 'September',
                'octobre' : 'October',
                'novembre' : 'November',
                'décembre' : 'December'}  

def format_date(df, col, dict_):
    date_list = df[col].tolist()
    new_date_list= []
    for el in date_list:
        for fr_word, en_word in dict_.items():
            if fr_word in el:
                el = el.strip().replace(fr_word, en_word)
        new_date_list.append(el)
    df['new_date'] = pd.Series(new_date_list)
    df['new_date'] = pd.to_datetime(df['new_date'], errors='coerce')
    return df

def mapper_df(df):
    mapper,s1, s2 = {},[],[]
    for el in df.columns[df.columns.str.startswith('sen_')]:
        s1.append(el)
        s2.append(el[4:])
    mapper = {k:v for k,v in zip(s1,s2)}
    df.rename(columns=mapper, inplace=True)
    return df

def mapper_series(serie):
    s = []
    for el in serie.index:
        s.append(el[4:])
    serie.index = s
    return serie

def genre(x):
    if x== "F":
        return "Femme"
    if x== "M":
        return "Homme"
    else:
        return "Non renseigné"

def create_pie(df):
    genre = df["genre"].value_counts()
    l1,l2 = [],[]
    for i in genre.values:
        l1.append(i)
    for j in genre.index:
        l2.append(j)
    return df, l1, l2

def graph_date_for_book(df, gender=None):
    df =  format_date(df, 'date', dict_mapping)
    df_date = df.sort_values('new_date')
    
    if gender is None:
        df_date = df_date[df_date['gender'] == gender]
    
    df_date["month"] =  df_date['new_date'].dt.month 
    df_date["year"] = df_date['new_date'].dt.year
    test = df_date.groupby(['year','month'])[['comm_id']].count().reset_index()
    test["Period"] = test['year'].astype(str) +"-"+ test["month"].astype(str)
    test["Period"] = pd.to_datetime(test["Period"]).dt.strftime('%Y-%m')
    if test['year'].max() - test['year'].min() > 6:
        test["Period"] = pd.to_datetime(test["Period"])
        test["Period"] = pd.to_datetime(test.groupby(pd.Grouper(key='Period', freq='6M')).sum().reset_index()['Period'])
    if test['year'].max() - test['year'].min() > 8 :
        test["Period"] = pd.to_datetime(test["Period"]).dt.strftime('%Y')
    fig = px.bar(test, x='Period', y='comm_id')
    return fig

def update_params_model(params_dic:dict, previous_dic):
    dic = previous_dic.copy()
    for key,value in params_dic.items():
        dic[key] = value
    return dic
