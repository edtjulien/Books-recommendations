from dash import Dash, html, dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

MOCKUP = [
    {
        'title' : "Fils de personne",
        'url' : "/livres/Pasques-Fils-de-personne/1466172",
        'image' : "https://m.media-amazon.com/images/I/51FlwT9EH2L._SX95_.jpg",
        'author' : "Jean-François Pasques",
        'author_url' : "http://www.google.fr"
    },
    {
        'title' : "La fille qui s’échappa d’Auschwitz",
        'url' : "/livres/Midwood-La-fille-qui-sechappa-dAuschwitz/1463048",
        'image' : "/couv/cvt_La-fille-qui-sechappa-dAuschwitz_8134.jpg",
        'author' : "Ellie Midwood",
        'author_url' : "http://www.google.fr"
    },
    {
        'title' : "Maple",
        'url' : "/livres/Goudreault-Maple/1467288",
        'image' : "https://m.media-amazon.com/images/I/41px-RwRutL._SX95_.jpg",
        'author' : "David Goudreault",
        'author_url' : "http://www.google.fr"
    },
    {
        'title' : "1629, Les Naufragés du Jakarta, tome 1 : L'apothicaire du Diable",
        'url' : "/livres/Dorison-1629-Les-Naufrages-du-Jakarta-tome-1--Lapothicai/1446523",
        'image' : "/couv/cvt_1629-Les-Naufrages-du-Jakarta-tome-1--Lapothicai_566.jpg",
        'author' : "Xavier Dorison",
        'author_url' : "http://www.google.fr"
    },
    {
        'title' : "Une saison pour les ombres",
        'url' : "/livres/Ellory-Une-saison-pour-les-ombres/1466915",
        'image' : "/couv/cvt_Une-saison-pour-les-ombres_145.jpg",
        'author' : "R. J. Ellory",
        'author_url' : "http://www.google.fr"
    },
]

URL_ROOT_WEBSITE = 'https://www.babelio.com'

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.read_json('../output/final/data-books.json', lines=True)
#df = pd.read_csv('./csv_files/julien1books_df.csv')
# preprocessing : dataframe avec seulement les colonnes que l'on a besoin
# todo, tester si image url commence par /

@app.callback(
    [Output('title', 'children'),
    Output('radar-map', 'figure'),
    Output('author', 'children'),
     Output('img-url', 'src'),
     Output('list-reco', 'children')],
   # [Input('input_search', 'value')],
    [Input('submit-search', 'n_clicks'),
    State('input-search', 'value')]
    #Output('map-spot', 'figure'),
)
def update_graph(n_clicks, search_value):
    if not search_value:
        search_value = "Quête de l'oiseau"

    df_found = df.loc[df['title'].str.contains(search_value, case=False)].reset_index()
    
    if df_found.shape[0] == 0:
        return 'Aucun livre trouvé'

    book = df_found.loc[0,:]
    title = book['title']
    author = book['surname'] + ' ' + book['name']
    img_url = book['img_url']
    if img_url.startswith('/'):
        img_url = URL_ROOT_WEBSITE + img_url

    book_id = book['book_id']

    df_radar=book[[col for col in df.columns if col.startswith('sen')]].T 

    fig_radar = px.line_polar(r = df_radar, # valeurs des axes du radar
                        theta = df_radar.index, # libellés des axes du radar
                        line_close = True, 
                        range_r=[0, max(df_radar)+0.1]) # valeurs minimum et maximum des axes

    recos = MOCKUP

    list_reco=[]
    for reco in recos:
        list_reco.append(html.Li(
            children=html.A(
                href=URL_ROOT_WEBSITE + reco["url"],
                target='_blank',
                children=reco["title"]
            )
        ))

    return title, fig_radar, author, img_url, list_reco


app.layout = html.Div(id='container-main', className='container-main', children=[


    html.Div(id='header-main', className='header-main', children=[
                html.Div(children=[
                        dcc.Input(
                            id="input-search",
                            className="input-text",
                            type='text',
                            placeholder="Chercher un livre",
                        ),

                        html.Button('Submit', id='submit-search', n_clicks=0),
                ]),
                html.H1(children='Books reco'),
    ]),

    html.Div(id='section-infos', className='section-infos section', children=[
        html.Div(id='book-details', className='book-details box-graph', children=[
            html.Div(id='title', children='', className='title'),
            html.Img(id='img-url', src=''),
            html.Div(id='author', children='', className='author'),
        ]),

        html.Div(id='book-sentiments', className='book-sentiments box-graph', children=[
            dcc.Graph(
                id='radar-map',
                figure={},
                responsive=True
            )
        ]),
    ]),

    html.Div(id='section-infos2', className='section-infos2 section', children=[
        html.Div(id='book-reco', className='book-reco box-graph', children=[
            html.Ul(
                id='list-reco',
                className='list-reco',
                children=[]
            )
        ]),

        html.Div(id='book-gender', className='book-gender box-graph', children=[
#            dcc.Graph(
#                id='___',
#                figure={},
#            )
        ]),

        html.Div(id='book-evolution', className='book-evolution box-graph', children=[
#            dcc.Graph(
#                id='___',
#                figure={},
            
#        )
        ],
        )]
    )


    
    # dcc.Dropdown(
    #     options=[
    #         {'label': 'New York City', 'value': 'NYC'},
    #         {'label': u'Montréal', 'value': 'MTL'},
    #         {'label': 'San Francisco', 'value': 'SF'}
    #     ],
    #     value=['MTL', 'SF'],
    #     multi=False,
    #     id='input'
    # ),

    # dcc.Graph(
    #     id='map-spot',
    #     figure={},
    # ),
])


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port="8050", debug=True)
