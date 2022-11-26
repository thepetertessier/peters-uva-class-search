# Visit http://127.0.0.1:8050/ when running locally

from dash import Dash, html, dcc
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
SAMPLE_SUBJECT = 'APMA'
SAMPLE_CATALOG_NUMBER = '1110'
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
    dbc.Row([
        dbc.Col(
            dbc.Row([
                html.Label('Term'),
                dcc.Dropdown(
                    id='term_dropdown',
                    options=terms,
                    value=terms[0],
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
                html.Label('Catalog #'),
                dcc.Input(
                    id='catalog_no_input',
                    value=SAMPLE_CATALOG_NUMBER,
                    style={'width': INPUT_WIDTH})
            ], justify='center', style={'margin-right': INPUT_PADDING}),
        ),

    ]),

], style={'textAlign': 'center', 'backgroundColor': colors['background']})


if __name__ == '__main__':
    app.run_server(debug=True)
