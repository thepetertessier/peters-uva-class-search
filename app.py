# Visit http://127.0.0.1:8050/ when running locally

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import requests
import pandas as pd

# Variables
tabtitle = 'UVA class search'
githublink = 'https://github.com/thepetertessier/peters-uva-class-search'
mywebsitelink = 'https://petertessier.com'
image = 'assets/uva_rotunda.png'

# Data
json_data = requests.get('https://api.devhub.virginia.edu/v1/courses').json()['class_schedules']
df = pd.DataFrame(json_data['records'], columns=json_data['columns'])

# Remove data we don't need
df = df.filter(items=['term_desc','subject', 'catalog_number', 'class_section',
                      'class_title', 'class_number', 'meeting_days',
                      'meeting_time_start', 'meeting_time_end', 'instructor'])

# Helper functions
def get_course(subject, catalog_number, term_desc):
    """
    Return df filtered based on subject, catalog_number, and term_desc

    :param subject: e.g., APMA
    :param catalog_number: e.g., 1110
    :param term_desc: e.g., 2022 Fall or 2023 Spring
    """
    return df[(df['subject'] == subject)
            & (df['catalog_number'] == catalog_number)
            & (df['term_desc'] == term_desc)]


# Initiate app
app = Dash(__name__)
server = app.server
app.title = tabtitle

colors = {
    'background': 'white',
    'theme': '#388ec7'
}

app.layout = html.Div([
    html.H1(
        children='UVA Class Search',
        style={
            'color': colors['theme']
        }
    )
], style={'textAlign': 'center', 'backgroundColor': colors['background']})

if __name__ == '__main__':
    app.run_server(debug=True)

