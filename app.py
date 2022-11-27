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
RECORDSLINK = 'https://api.devhub.virginia.edu/v1/courses'
IMAGE = 'assets/uva_background.png'

# Constants for Input fields
SAMPLE_SUBJECT = None
SAMPLE_CATALOG_NUMBER = ''
INPUT_WIDTH = '150px'
INPUT_PADDING = 300

# Data
json_data = requests.get(RECORDSLINK).json()['class_schedules']
df = pd.DataFrame(json_data['records'], columns=json_data['columns'])
terms = list(dict.fromkeys(df['term_desc'])) # e.g., ['Fall 2022','Spring 2023']
subjects = list(dict.fromkeys(df['subject'])) # e.g., ['APMA','CS',...]

# Remove data we don't need
df = df.filter(items=['term_desc','subject', 'catalog_number', 'class_section',
                      'class_title', 'class_number', 'meeting_days',
                      'meeting_time_start', 'meeting_time_end', 'instructor'])

# Helper functions
def get_course(this_df, term_desc, subject, catalog_number):
    """
    Return df filtered based on term_desc, subject, catalog_number

    :param term_desc: e.g., 2022 Fall or 2023 Spring
    :param subject: e.g., APMA
    :param catalog_number: e.g., 1110
    """
    return this_df[(this_df['term_desc'] == term_desc)
                 & (this_df['catalog_number'] == catalog_number)
                 & (this_df['subject'] == subject)]


# Initiate app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = TABTITLE

colors = {
    'background': 'white',
    'theme': '#388ec7'
}

app.layout = html.Div([
    html.Img(src=IMAGE, height=200),
    html.Br(),
    dbc.Row(
        dbc.Col([
            html.Br(),
            dbc.Alert([
                html.P('Welcome to my UVA Class Search!'),
                html.P('To search for a given class, simply input the term, subject, and catalog number'),
                html.Br(),
                html.P('Term: (optional) year and season (e.g., Spring 2023)', style={'text-align':'left'}),
                html.P('Subject: (required) 2-4 letters denoting subject (e.g., APMA)', style={'text-align':'left'}),
                html.P('Catalog number: (optional) 4 digits specifying which class given the subject (e.g., 1110)', style={'text-align':'left'})
                ],
                color='primary',
                dismissable=True
            )], width={'size':6, 'offset':3}
        )
    ),
    dbc.Row([
        dbc.Col(
            dbc.Row([
                html.Label('Term'),
                dcc.Dropdown(
                    id='term_dropdown',
                    options=terms)
            ], justify='center'),
            width={'size':2,'offset':3}),
        dbc.Col(
            dbc.Row([
                html.Label('Subject'),
                dcc.Dropdown(
                    id='subject_dropdown',
                    options=subjects,
                    value=SAMPLE_SUBJECT,)
            ], justify='center'),
            width={'size':2,'offset':0}
        ),
        dbc.Col(
            dbc.Row([
                html.Label('Catalog # (1110)'),
                dcc.Input(
                    id='catalog_no_input',
                    value=SAMPLE_CATALOG_NUMBER,
                    debounce=True,
                    style={'width': INPUT_WIDTH})
            ], justify='center'),
            width={'size':2, 'offset':0}
        ),
    ]),
    html.Br(),
    html.Button('Search', id='search_button', n_clicks=0, disabled=False),
    html.Br(),
    html.Br(),
    html.Div(children='',id='output'),
    html.Br(),
    html.Br(),
    html.A('Raw class records', href=RECORDSLINK),
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
    Input('catalog_no_input', 'value'),
    Input('search_button','n_clicks')
)
def create_class_info_table(term, subject, catalog_no, n_clicks):
    if n_clicks == 0:
        return html.Br()

    term_exists = not (term == None)
    subject_exists = not (subject == None)
    catalog_no_exists = not (catalog_no == '')

    if not subject_exists:
        return html.H6('Please input a subject.')

    # Replace nonexistant term and catalog_no so that their final comparison will always be true
    if not term_exists:
        term = df['term_desc']
    if not catalog_no_exists:
        catalog_no = df['catalog_number']

    # Filter df to just that course
    course_df = get_course(df, term, subject, catalog_no)

    if course_df.empty:
        return html.H6('No class with that term, subject, and/or catalog number')

    # Drop the columns we don't need
    course_df.drop('subject', axis=1, inplace=True)
    if term_exists:
        course_df.drop('term_desc', axis=1, inplace=True)
    if catalog_no_exists:
        course_df.drop('catalog_number', axis=1, inplace=True)

        # Head the table with e.g. 'Discrete Math and Theory I | CS 2120' or just 'CS 2120'
        table_header = '%s | %s %s' % (course_df['class_title'].iloc[0], subject, catalog_no)
        course_df.drop('class_title', axis=1, inplace=True)
    else:
        table_header = '%s' % subject

    if term_exists:
        table_header += ' (%s)' % term

    # Rename columns for user
    course_df.rename(columns={'term_desc':'Term', 'catalog_number': 'Catalog #',
                              'class_section': 'Class section', 'class_title': 'Class Title',
                              'class_number': 'Class #', 'meeting_days': 'Meeting days',
                              'meeting_time_start': 'Start time', 'meeting_time_end': 'End time',
                              'instructor': 'Instructor'}, inplace=True)

    # Finally, return dataframe as DataTable
    return html.Div([
        html.H6(table_header, style={'text-align': 'left', 'margin-left': 10}),
        dash_table.DataTable(course_df.to_dict('records'), [{"name": i, "id": i} for i in course_df.columns])
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
