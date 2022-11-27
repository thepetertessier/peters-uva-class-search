# Visit http://127.0.0.1:8050/ when running locally

from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import requests
import pandas as pd

# Constants
TABTITLE = 'UVA class search'
GITHUBLINK = 'https://github.com/thepetertessier/peters-uva-class-search'
MYWEBSITELINK = 'https://petertessier.com'
IMAGE = 'assets/uva_rotunda.png'

# Constants for Input fields
SAMPLE_SUBJECT = None
SAMPLE_CATALOG_NUMBER = ''
INPUT_WIDTH = '150px'
INPUT_PADDING = 300

# Data
json_data = requests.get('https://api.devhub.virginia.edu/v1/courses').json()['class_schedules']
df = pd.DataFrame(json_data['records'], columns=json_data['columns'])
terms = list(dict.fromkeys(df['term_desc'])) # e.g., ['Fall 2022','Spring 2023']
subjects = list(dict.fromkeys(df['subject'])) # e.g., ['APMA','CS',...]

# Remove data we don't need
df = df.filter(items=['term_desc','subject', 'catalog_number', 'class_section',
                      'class_title', 'class_number', 'meeting_days',
                      'meeting_time_start', 'meeting_time_end', 'instructor'])

# Helper functions
def get_course(term_desc, subject, catalog_number):
    """
    Return df filtered based on term_desc, subject, catalog_number

    :param term_desc: e.g., 2022 Fall or 2023 Spring
    :param subject: e.g., APMA
    :param catalog_number: e.g., 1110
    """
    # Replace nonexistant term_desc and catalog_no so that their final comparison will always be true
    if term_desc == None:
        term_desc = df['term_desc']
    if catalog_number == '':
        catalog_number = df['catalog_number']

    return df[(df['term_desc'] == term_desc)
            & (df['catalog_number'] == catalog_number)
            & (df['subject'] == subject)]


# Initiate app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = TABTITLE

colors = {
    'background': 'white',
    'theme': '#388ec7'
}

app.layout = html.Div([
    html.H1(
        children='UVA Class Search',
        style={
            'color': colors['theme'],
            # 'background-image': IMAGE
        }
    ),
    html.Img(src=IMAGE, height=110),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Row([
                html.Label('Term'),
                dcc.Dropdown(
                    id='term_dropdown',
                    options=terms,
                    style={'width': INPUT_WIDTH}
                )
            ], justify='center', style={'margin-left': INPUT_PADDING})
        ),
        dbc.Col(
            dbc.Row([
                html.Label('Subject'),
                dcc.Dropdown(
                    id='subject_dropdown',
                    options=subjects,
                    value=SAMPLE_SUBJECT,
                    style={'width': INPUT_WIDTH})
            ], justify='center'),
        ),
        dbc.Col(
            dbc.Row([
                html.Label('Catalog # (1010)'),
                dcc.Input(
                    id='catalog_no_input',
                    value=SAMPLE_CATALOG_NUMBER,
                    style={'width': INPUT_WIDTH})
            ], justify='center', style={'margin-right': INPUT_PADDING}),
        ),
    ]),
    html.Br(),
    html.Button('Search', id='search_button', n_clicks=0, disabled=False),
    html.Br(),
    html.Br(),
    html.Div(children='',id='output'),
    html.Br(),
    html.Br(),
    html.A('Code on GitHub', href=GITHUBLINK),
    html.Br(),
    html.A('About me', href=MYWEBSITELINK)
], style={'textAlign': 'center', 'backgroundColor': colors['background']})


# If the button is clicked, return table of given class
@app.callback(
    Output('output','children'),
    State('term_dropdown', 'value'),
    State('subject_dropdown', 'value'),
    State('catalog_no_input', 'value'),
    Input('search_button','n_clicks')
)
def create_class_info_table(term, subject, catalog_no, n_clicks):
    if n_clicks == 0:
        return html.Br()

    if subject == None:
        return html.H6('Please input a subject.')

    course_df = get_course(term, subject, catalog_no)
    return dash_table.DataTable(course_df.to_dict('records'), [{"name": i, "id": i} for i in course_df.columns])

if __name__ == '__main__':
    app.run_server(debug=True)
