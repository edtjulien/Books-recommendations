import pandas as pd
import math
import config

# sépare le dataframe en n elements dans un dictionnaire. n est la longueur de list_split et la clé dans le dictionnaire est la valeur de l'elt du list_split
def split_dataframe(df, list_split):
    size_split = len(list_split)
    size_df = df.shape[0]

    cut_size = math.floor(size_df / size_split)

    dic = {}
    for i, name in enumerate(list_split):
        if i < size_split - 1:
            new_df = df.iloc[i*cut_size:((i+1)*cut_size),:].copy()
        else: new_df = df.iloc[i*cut_size:,:].copy()

        dic = {**dic, name: new_df}

    return dic

if __name__ == "__main__":
    df = pd.read_json(config.LIST_BOOKS_FILE, lines=True)

    nb_rows = df.shape[0]
    df = df.drop_duplicates(subset = "book_id", keep = 'first')
    print("Suppression de",nb_rows - df.shape[0], "livres dubliqués")

    df = df.sample(frac=1) # shuffle rows
    print('Mélange aléatoire des lignes')
    
    list_df = split_dataframe(df, config.SPLITER_LIST)

    for name,data in list_df.items():
        data.to_json(config.SPLITER_FILE.format(name), orient='records', lines=True)
    print("Partage des listes selon :", ",".join(config.SPLITER_LIST))
