from dash import Dash, html, dcc, html, Input, Output, State
import utils
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df_books = pd.read_json('../output/final/data-books.json', lines=True)
df_comms = pd.read_json('../output/final/data-comm.json', lines=True)
df_comms = utils.format_date(df_comms, 'date', utils.dict_mapping)

@app.callback(
    [Output('subtitle', 'children'),
     Output('radar-map', 'figure'),
     Output('date-map', 'figure'),
     Output('genre-map', 'figure')],
   # [Input('input_search', 'value')],
    [Input('submit-search', 'n_clicks'),
    State('input-search', 'value')]
)

def update_graph(n_clicks, search_value):
    if not search_value:
        search_value = "Quête de l'oiseau"

    df_found = df_books.loc[df_books['title'].str.contains(search_value, case=False)].reset_index()
    
    if df_found.shape[0] == 0:
        return 'Aucun livre trouvé'

    book = df_found.loc[0,:]
    title = book['title']
    book_id = book['book_id']

    df_radar = book[[col for col in df_books.columns if col.startswith('sen')]].T 
    df_radar = utils.mapper_series(df_radar)

    fig_radar = px.line_polar(r = df_radar, # valeurs des axes du radar
                        theta = df_radar.index, # libellés des axes du radar
                        line_close = True, 
                        range_r=[0, max(df_radar)+0.1]) # valeurs minimum et maximum des axes
    fig_radar.update_traces(fill='toself')

    fig_date = utils.graph_date_for_book(df_comms, title)

    df_gender = df_comms[df_comms['book_id'] == book_id]
    df_gender["genre"] = df_gender["gender"].apply(utils.genre)
    df_gender,l1,l2 = utils.create_pie(df_gender)

    fig_genre = px.pie(values=l1, names=l2, title='répartition des hommes et des femmes', color_discrete_sequence=px.colors.sequential.ice)
    

    return [f'Titre du livre: {title} avec l\'id {book_id}'], fig_radar, fig_date, fig_genre


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
                responsive=True,
                id='radar-map',
                figure={},
            )
        ]),
    ]),

    html.Div(id='section-infos2', className='section-infos2 section', children=[
        html.Div(id='book-reco', className='book-reco box-graph', children=[
            
        ]),

        html.Div(id='book-gender', className='book-gender box-graph', children=[
            dcc.Graph(
                responsive=True,
                id='genre-map',
                figure={},
            )
        ]),

        html.Div(id='book-evolution', className='book-evolution box-graph', children=[
            dcc.Graph(
                responsive=True,
                id='date-map',
                figure={},
            
        )
        ]
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
