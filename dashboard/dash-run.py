from dash import Dash, html, dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.read_json('../output/final/data-books.json', lines=True)

@app.callback(
    [Output('subtitle', 'children')],
   # [Input('input_search', 'value')],
    Input('submit-search', 'n_clicks'),
    State('input-search', 'value')
    #Output('map-spot', 'figure'),
)
def update_graph(n_clicks, text):
    if not text:
        return ['']
    df_found = df.loc[df['title'].str.contains(text, case=False)].reset_index()
    title = 'Aucun livre trouvé'
    if df_found.shape[0] > 0:
        title = df_found.loc[0,'title']
    return [f'Titre du livre: {title}']


app.layout = html.Div(children=[
    html.H1(children='Books reco'),

    dcc.Input(
            id="input-search",
            type='text',
            placeholder="Chercher un livre",
        ),
    html.Button('Submit', id='submit-search', n_clicks=0),

    html.Div(id='subtitle', children=[], className='sub-title'),

    # dcc.Graph(
    #     id='map-spot',
    #     figure={},
    # ),
])


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port="8050", debug=True)
