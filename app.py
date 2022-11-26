import requests
import pandas as pd

def get_json():
	url = 'https://api.devhub.virginia.edu/v1/courses'
	return requests.get(url).json()

def get_df():
    data = get_json()['class_schedules']
    return pd.DataFrame(data['records'], columns=data['columns'])

df = get_df()

def get_course(subject, catalog_number, term_desc):
    """
    Return df filtered based on subject, catalog_number, and term_desc

    :param subject: e.g., APMA
    :param catalog_number: e.g., 1110
    :param term_desc: e.g., 2022 Fall or 2023 Spring
    """
    return df[(df['subject'] == subject) & (df['catalog_number'] == catalog_number) & (df['term_desc'] == term_desc)]

print(df.columns)
print(get_course('APMA','2120','2022 Fall').filter(items=['class_section','class_number','instructor']))
pass
