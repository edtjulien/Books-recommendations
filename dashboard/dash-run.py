from dash import Dash, html, dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# df = pd.read_json('./csv_files/data-books.json', lines=True)
df = pd.read_csv('./csv_files/julien1books_df.csv')
# preprocessing : dataframe avec seulement les colonnes que l'on a besoin

@app.callback(
    [Output('subtitle', 'children'),
     Output('radar-map', 'figure')],
   # [Input('input_search', 'value')],
    [Input('submit-search', 'n_clicks'),
    State('input-search', 'value')]
    #Output('map-spot', 'figure'),
)
def update_graph(n_clicks, search_value):
    if not search_value:
        return ['']

    df_found = df.loc[df['title'].str.contains(search_value, case=False)].reset_index()
    
    if df_found.shape[0] == 0:
        return 'Aucun livre trouvé'

    book = df_found.loc[0,:]
    title = book['title']
    book_id = book['book_id']

    df_radar=book[[col for col in df.columns if col.startswith('sen')]].T 
    print(df_radar)
    
    print("index radar:",df_radar.index)
    print("sentiments:",df_radar)

    fig_radar = px.line_polar(r = df_radar, # valeurs des axes du radar
                        theta = df_radar.index, # libellés des axes du radar
                        line_close = True, 
                        range_r=[0, max(df_radar)+0.1]) # valeurs minimum et maximum des axes
    

    return [f'Titre du livre: {title} avec l\'id {book_id}'], fig_radar


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
            html.Div(id='subtitle', children=[], className='sub-title'),
        ]),

        html.Div(id='book-sentiments', className='book-sentiments box-graph', children=[
            dcc.Graph(
                id='radar-map',
                figure={},
            )
        ]),
    ]),

    html.Div(id='section-infos2', className='section-infos2 section', children=[
        html.Div(id='book-reco', className='book-reco box-graph', children=[
            
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
