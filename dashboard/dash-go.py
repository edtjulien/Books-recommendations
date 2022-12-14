from dash import Dash, html, dcc, html, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import dill
import sqlite3
import warnings
import utils
import modelreco
from config import DEFAULT_BOOK_ID, DEFAULT_MODEL_PARAMS, MAX_TO_PREDICT, URL_ROOT_WEBSITE, MODEL_FILE, SERVER_PORT, DB_FILE

warnings.filterwarnings('ignore') 

# https://fizzy.cc/deploy-dash-on-server/
# gunicorn dash-go:server -b :8080 &

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

with open(MODEL_FILE, 'rb') as f:
    model = dill.load(f)

#df_books = pd.read_json(BOOK_FILE, lines=True)
#df_comms = pd.read_json(COMM_FILE, lines=True)

def get_data_byid(table, book_id, books_id_list=None):
    conn = sqlite3.connect(DB_FILE)
    if books_id_list is not None:
        sql_query = pd.read_sql(f'SELECT * FROM {table} WHERE book_id IN ({ ",".join(books_id_list) })', conn)
    else: sql_query = pd.read_sql(f'SELECT * FROM {table} WHERE book_id="{book_id}"', conn)
    conn.close()
    return pd.DataFrame(sql_query)

def get_data_search(table, col_search, value):
    conn = sqlite3.connect(DB_FILE)
    sql_query = pd.read_sql(f'SELECT book_id, title, book_rating_value FROM {table} WHERE LOWER({col_search}) like "%{value.lower()}%" ORDER BY book_rating_value DESC', conn)
    conn.close()
    return pd.DataFrame(sql_query)
 
def make_list_reco_html(list_json):
    list_reco=[]
    for reco in list_json:
        img_url = reco["image"]
        if img_url.startswith('/'):
            img_url = URL_ROOT_WEBSITE + img_url
        list_reco.append(html.Li(
            children=html.A(
                href=reco["url"],
                target='_blank',
                children=[
                    html.Img(src=img_url),
                    html.Div(children=[reco["title"]])
                ],
            )
        ))
    return list_reco

def predict_reco(book_id, model_params):
    global model
    model.set_weight(model_params)
    scores = model.predict(int(book_id))
    books_id_list = [str(bid) for bid in list(scores.index)]
    df_books_reco = get_data_byid('books', None, books_id_list=books_id_list)
    res = model.format_tojson(scores, df_books_reco, max_books=MAX_TO_PREDICT)
    list_reco = make_list_reco_html(res)

    return list_reco

@app.callback(
    Output("offcanvas", "is_open"),
    Output('book-details', 'children'),
    Output('radar-map', 'figure'),
    Output('list-reco', 'children'),
    Output('date-map', 'figure'),
    Output('genre-map', 'figure'),
    Input("drop-search", "value"),
    Input("open-params", "n_clicks"),
    Input("submit-model", "n_clicks"),
    [State("slider-sen", "value"),
    State("slider-jaccard", "value"),
    State("slider-tags", "value"),
    State("slider-rating", "value"),
    State("slider-users", "value"),
    ]
)
def update_graph(book_id, n_clicks1, n_clicks2, param_sen, param_jaccard, param_tags, param_rating, param_users):
    if book_id is None:
        book_id = DEFAULT_BOOK_ID
        #raise PreventUpdate

    is_open_offset = False

    # if toggle param
    button_id = ctx.triggered_id if not None else 'No clicks yet'
    if button_id == 'open-params':
        is_open_offset = True
    if button_id == 'submit-model':
        is_open_offset = False

    model_params = utils.update_params_model({
        'sen_':param_sen,
        'tag_':param_tags,
        'jaccard':param_jaccard,
        'book_rating_value':param_rating,
        'users':param_users,
    }, DEFAULT_MODEL_PARAMS)
        

    # end if

    book = get_data_byid('books', book_id).iloc[0,:]

    title = book['title']
    author = book['surname'] + ' ' + book['name']
    book_rating_value = str(round(book['book_rating_value'],1)) + ' / 5'
    book_rating_count = ' (' + str(book['book_rating_count']) + ' notes)'
    url = book['book_url']
    author_url = book['book_author_url']
    if author_url.startswith('/'):
            author_url = URL_ROOT_WEBSITE + author_url
    img_url = book['img_url']
    if img_url.startswith('/'):
        img_url = URL_ROOT_WEBSITE + img_url

    df_radar = book[[col for col in book.index if col.startswith('sen')]].T 
    df_radar = utils.mapper_series(df_radar)

    fig_radar = px.line_polar(r = df_radar, # valeurs des axes du radar
                        theta = df_radar.index, # libellés des axes du radar
                        line_close = True, 
                        range_r=[0, max(df_radar)+0.1]) # valeurs minimum et maximum des axes
    fig_radar.update_traces(fill='toself')

    # START
    dfc = get_data_byid('comm', book_id)
    fig_date = utils.graph_date_for_book(dfc, title)

    dfc["genre"] = dfc["gender"].apply(utils.genre)
    _ , l1, l2 = utils.create_pie(dfc)

    fig_genre = px.pie(values=l1, names=l2)
    # END

    list_reco = predict_reco(book_id, model_params)

    book_details = [html.Div(id='title', children=[html.A(href=url, children=title, target='_blank')], className='title'),
                    html.Div(id='author', children=html.A(href=author_url, children=author, target='_blank'), className='author'),
                    html.Img(id='img-url', src=img_url),
                    html.Div(children=[
                        html.Span(id='rating-value', children=book_rating_value, className='rating-value'),
                        html.Span(id='rating-count', children=book_rating_count, className='rating-count')
                        ])
                    ]

    return is_open_offset, book_details, go.FigureWidget(fig_radar), list_reco, go.FigureWidget(fig_genre), go.FigureWidget(fig_date)

@app.callback(
    Output("drop-search", "options"),
    Input("drop-search", "search_value")
)
def update_options(search_value):
    if not search_value or len(search_value) < 3:
        raise PreventUpdate
    
    df_found = get_data_search('books', 'title', search_value) # check if needed to preprocess search_value to prevent sql injection

    if df_found.shape[0] > 0:
        df_found['title'] = df_found.apply(lambda book: book['title'] + ' (' + str(round(book['book_rating_value'],1)) + '/5)', axis=1)
        df_found = df_found[['title','book_id']]
        df_found.columns = ['label','value']
        df_found = df_found.to_dict('records')
    else:
        return []

    return df_found

app.layout = html.Div(id='container-main', className='container-main', children=[
    dbc.Offcanvas(
            html.Div(id='params',children=[
                html.P("Réglages des paramètres du modèle de recommandation :", className='subtitle-params'),
                html.P('Sentiments', className='title-params'),
                dcc.Slider(0, 100, 1, value=DEFAULT_MODEL_PARAMS['sen_'], id='slider-sen', marks=None),
                html.P('Similarité vocabulaire', className='title-params'),
                dcc.Slider(0, 100, 1, value=DEFAULT_MODEL_PARAMS['jaccard'], id='slider-jaccard', marks=None),
                html.P('Thèmes', className='title-params'),
                dcc.Slider(0, 100, 1, value=DEFAULT_MODEL_PARAMS['tag_'], id='slider-tags', marks=None),
                html.P('Notes', className='title-params'),
                dcc.Slider(0, 100, 1, value=DEFAULT_MODEL_PARAMS['book_rating_value'], id='slider-rating', marks=None),
                html.P('Communauté', className='title-params'),
                dcc.Slider(0, 100, 1, value=DEFAULT_MODEL_PARAMS['users'], id='slider-users', marks=None),
                dbc.Button('Mettre à jour le modèle', color="secondary", id='submit-model', n_clicks=0, className="me-1 param-button"),
            ]
            ),
            id="offcanvas",
            title="Paramètres du modèle",
            placement='end',
            is_open=False,
        ),

    html.Div(id='header-main', className='header-main', children=[
                
                html.Img(src='assets/logo-book.png', className='logo'),
    ]),

    html.Div(id='header-search', className='header-search', children=[
                
                html.Div(children=[
                        html.Div(id='search-label', children='Rechercher un livre'),
                        dcc.Dropdown(
                            id='drop-search',
                            optionHeight=60,
                            multi=False,
                            value=DEFAULT_BOOK_ID
                        ),
                ]),
                
    ]),

    html.Div(id='section-infos', className='section-infos section', children=[
        html.Div(id='book-details', className='book-details box-graph', children=[
            
        ]),

        html.Div(id='book-reco', className='book-reco box-graph', children=[
            html.Div(className='head-box', children=['Recommandations',
                dbc.Button('Paramètres', color="secondary", id='open-params', n_clicks=0, className="me-1 btn-sm param-button")]),
            html.Ul(
                id='list-reco',
                className='list-reco',
                children=[]
            )
        ]),

        html.Div(id='book-sentiments', className='book-sentiments box-graph', children=[
            html.Div(className='head-box', children='Radar des sentiments'),
            dcc.Graph(
                id='radar-map',
                figure={},
                responsive=True
            )
        ]),
    ]),

    html.Div(id='section-infos2', className='section-infos2 section', children=[

        html.Div(id='book-gender', className='book-gender box-graph', children=[
            html.Div(className='head-box', children='Evolution temporelle des commentaires'),
            dcc.Graph(
                    responsive=True,
                    id='genre-map',
                    figure={},
                )
        ]),

        html.Div(id='book-evolution', className='book-evolution box-graph', children=[
            html.Div(className='head-box', children='Répartition des hommes et des femmes'),
            dcc.Graph(
                responsive=True,
                id='date-map',
                figure={},
        )],
        )]
    ),

    html.Div(id='footer', className='footer', children=['By Rebecca, Antoine, David, Julien']),
]) 


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=SERVER_PORT, debug=True)
