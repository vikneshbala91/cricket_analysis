import requests
from bs4 import BeautifulSoup

WEBSITE = "https://www.cricbuzz.com"
BASE_URL = "https://www.cricbuzz.com/cricket-scorecard-archives/"

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
            'duration_text': x.contents[1].text,
            'href': WEBSITE + x.contents[0]['href']
            }
        series_list.append(row)
    return series_list