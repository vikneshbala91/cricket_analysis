import requests
from bs4 import BeautifulSoup
import pandas as pd
from config import WEBSITE, BASE_URL, extract_series_info
from datetime import datetime
import time

def extract_tournament_matches(tour_url):
    page = requests.get(tour_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    tour_match_list = []
    for grp in soup.find_all('div',{'class':'cb-col-100'}):
        if grp.find('div',{'class':'schedule-date'}) != None:
            schedule_object = grp.find('div',{'class':'schedule-date'}).find_all('span')
            if len(schedule_object) != 0:
                match_schedule_ts = [x['ng-bind'].split('|')[0].strip()[:-3] for x in schedule_object]
                match_schedule = [datetime.utcfromtimestamp(int(x)).strftime('%Y-%m-%d') for x in match_schedule_ts]
                if len(match_schedule) == 2:
                    match_days = str(match_schedule[0]) + " | " + str(match_schedule[1])
                else: 
                    match_days = str(match_schedule[0])
            match_details_object = grp.find('div',attrs={'class':'cb-col-60'})
            # handling match_href issue
            match_href_object = match_details_object.find('a',attrs={'class':"text-hvr-underline"})
            if match_href_object is None:
                break
            else:
                match_href = match_href_object['href']
            # handling None issue for future matches
            match_result_object = match_details_object.find('a',attrs={'class':"cb-text-complete"})
            match_result = match_result_object.text if match_result_object != None else None
            row = {
                'match_days' : match_days,
                'match_href' : WEBSITE + match_details_object.find('a',attrs={'class':"text-hvr-underline"})['href'],
                'match_title' : match_details_object.find('a',attrs={'class':"text-hvr-underline"}).text,
                'match_result' : match_result,
                'match_ground' : match_details_object.div.text.split(", ")[0],
                'match_location' : match_details_object.div.text.split(", ")[1]           
            }
            tour_match_list.append(row)   
    return tour_match_list

def run(first_iteration = True):
    error_url = []
    if first_iteration:
        series_df = pd.read_csv("../data_dir/tournament_tb.csv")
        tour_match_df = pd.DataFrame(None,columns=['match_days','match_href','match_title',
                                              'match_result','match_ground', 'match_location'])
        first_iteration=False
    for idx, row in series_df.iterrows():
        print(row['title'])
        try:
            tour_match_df = tour_match_df.append(extract_tournament_matches(row['href']),ignore_index=True)
        except:
            try:
                time.sleep(30)
                tour_match_df = tour_match_df.append(extract_tournament_matches(row['href']),ignore_index=True)
            except:
                print('failed in second attempt as well')
                print(row['href'])
                error_url.append(row['href'])
    # trying the errored one again to resolve the connectivity issue
    error_list_empty, max_loop = False, 10
    i = 1
    while (not error_list_empty) and (i != max_loop):
        print('RETRYING ATTEMPT - ', i) 
        new_error_url = []
        for url in error_url:
            try:
                tour_match_df = tour_match_df.append(extract_tournament_matches(url),ignore_index=True)
            except:
                print('failed url :', url)
                new_error_url.append(url)
        if len(new_error_url) == 0:
            error_list_empty = True
        else:
            error_url = new_error_url
            i += 1
            time.sleep(30)
    tour_match_df.to_csv("../data_dir/tour_match_tb.csv",index=False)

if __name__ == "__main__":
	run()