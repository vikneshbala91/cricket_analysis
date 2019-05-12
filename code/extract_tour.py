import requests
from bs4 import BeautifulSoup
import pandas as pd
from config import WEBSITE, BASE_URL

def extract_series_info(year):
    '''
    input: year
    returns dataframe with series name and time it happened with url for further details
    '''
    page = requests.get(BASE_URL+str(year))
    main_soup = BeautifulSoup(page.content, 'html.parser')
    # always fetch first class element with value 'cb-col-84' which gives INTERNATIONAL 
    series_box = main_soup.find('div',attrs={'class':'cb-col-84'})
    series_list = []
    for x in series_box.children:
        row={
            'title': x.contents[0].text,
            'year': year,
            'duration_text': x.contents[1].text,
            'href': WEBSITE + x.contents[0]['href']
            }
        series_list.append(row)
    return series_list

def append_series_info(df, year):
    'adds the new year data to the existing series dataframe'
    return df.append(extract_series_info(year))

def run():
    First_iteration=True
    for x in range(1990,2020):
        if First_iteration:
            series_df = pd.DataFrame(None, columns=['title', 'year', 'duration_text', 'href'])
            First_iteration=False
        series_df = series_df.append(extract_series_info(x))
    series_df.to_csv("../data_dir/tour_tb.csv",index=False)

if __name__ == "__main__":
    run()