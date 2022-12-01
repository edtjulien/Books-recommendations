from dash import Dash, html, dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.read_json('../output/final/data-books.json', lines=True)

@app.callback(
    [Output('subtitle', 'children'),
    Output('gender-pie', 'figure')
    ],
   # [Input('input_search', 'value')],
    Input('input-search', 'value'),
    #State('input-search', 'value')
    #Output('map-spot', 'figure'),
)
def update_graph(text):
    if not text:
        return ['']
    df_found = df.loc[df['title'].str.contains(text, case=False)].reset_index()
    title = 'Aucun livre trouvé'
    if df_found.shape[0] > 0:
        title = df_found.loc[0,'title']

    book_id = df_found.loc[0,'book_id']

    fig = px.pie(df[df['book_id'] == book_id], sdlf)
        
    return [f'Titre du livre: {title}'], fig


app.layout = html.Div(children=[
    html.H1(children='Books reco'),

    dcc.Input(
            id="input-search",
            type='text',
            value='to',
            placeholder="Chercher un livre",
        ),
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
    #html.Button('Submit', id='submit-search', n_clicks=0),

    html.Div(id='subtitle', children=[], className='sub-title'),

    dcc.Graph(
        id='gender-pie',
        figure={},
    ),
])


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port="8050", debug=True)
