import requests
from bs4 import BeautifulSoup
from datetime import datetime
from src.config import BASE_URL, MAIN_WEBSITE, MIN_SERIES_YEAR
from src.collection_schema import TOURNAMENT, MATCH


class CricketDatabase:
    def __init__(self):
        print("Cricket database sourced from cricbuzz")

    def _extract_tournament(self, last_extracted_series = None):
        """
        :param LAST_SERIES:
        :return:
        """
        last_extracted_series = last_extracted_series.strip() if last_extracted_series is not None else None
        data_extracted = False
        tournament_data_list, tournament_links, tournament_count = [], {}, 0
        year = int(datetime.now().year)

        while year >= MIN_SERIES_YEAR and not data_extracted:
            print('extracting tournaments of {}'.format(year))
            page = requests.get(BASE_URL + str(year))
            main_soup = BeautifulSoup(page.content, 'html.parser')
            tour_level = main_soup.findAll('h2', attrs={"class": "cb-lv-scr-mtch-hdr"})
            tour_level = [t.text for t in tour_level]
            tour_information = main_soup.findAll('div', attrs={"class": "cb-col-84"})
            for tour_type, tour_info in zip(tour_level, tour_information):
                for tour in tour_info.children:
                    collection_json = {}
                    collection_json[TOURNAMENT.tournament_type] = tour_type
                    collection_json[TOURNAMENT.tournament_title] = tour.contents[0].text.strip()
                    collection_json[TOURNAMENT.tournament_year] = year
                    collection_json[TOURNAMENT.tournament_start_month] = tour.contents[1].text.strip()
                    collection_json[TOURNAMENT.tournament_end_month] = tour.contents[1].text.strip()
                    collection_json[TOURNAMENT.tournament_link] = tour.contents[0]['href']
                    data_extracted = True if collection_json[TOURNAMENT.tournament_title] == \
                                             last_extracted_series else False
                    if data_extracted:
                        break
                    tournament_count += 1
                    tournament_data_list.append(collection_json)
                    tournament_links.update({tournament_count: collection_json[TOURNAMENT.tournament_link]})
                if data_extracted:
                    break
            year = year - 1
        return tournament_data_list, tournament_links

    def _extract_tournament_matches(self, tournament_link, match_count):
        print(tournament_link)
        page = requests.get(MAIN_WEBSITE + tournament_link)
        main_soup = BeautifulSoup(page.content, 'html.parser')
        match_details = main_soup.findAll('div', attrs={"class": "cb-series-matches"})
        tournament_matches_list, tournament_match_links = [], {}
        for match_box in match_details:
            collection_json = {}
            match_box_1 = match_box.findAll('div', attrs={"class": "schedule-date"})
            match_start_end_date = []
            for xx in match_box_1:
                match_start_end_date = [str(datetime.fromtimestamp(int(x['ng-bind'].split('|')[0].strip()[:-3]))).split(" ")[0]
                                        for x in xx.findAll('span')]
                match_start_date = match_start_end_date[0]
                match_end_date = match_start_end_date[1] if len(match_start_end_date) == 2 else match_start_end_date[0]

            match_box_2 = match_box.find('div', attrs={"class": "cb-col-60"}).contents
            if match_box.find('a', attrs={"class": "cb-text-inprogress"}) is not None:
                match_result = match_box.find('a', attrs={"class": "cb-text-inprogress"}).text
            elif match_box.find('a', attrs={"class": "cb-text-complete"}) is not None:
                match_result = match_box.find('a', attrs={"class": "cb-text-complete"}).text
            else:
                match_result = None
            match_box_3 = match_box.find('div', attrs={"class": "cb-font-12"}).contents
            collection_json[MATCH.match_link] = match_box_2[0]['href']
            collection_json[MATCH.match_title] = match_box_2[0].text
            collection_json[MATCH.match_place] = match_box_2[1].text
            collection_json[MATCH.match_result] = match_result
            collection_json[MATCH.match_time_gmt] = match_box_3[0].text.strip() \
                if match_box_3[1] == 'GMT	/' else None
            collection_json[MATCH.match_time_local] = match_box_3[2].text.strip() \
                if match_box_3[3] == ' LOCAL' else None
            collection_json[MATCH.match_start_date] = match_start_date
            collection_json[MATCH.match_end_date] = match_end_date
            match_count += 1
            tournament_matches_list.append(collection_json)
            tournament_match_links.update({match_count: match_box_2[0]['href']})

        return tournament_matches_list, tournament_match_links

    def run(self, last_extracted_series):
        tournament_data_list, tournament_links = self._extract_tournament(last_extracted_series=last_extracted_series)

        tournament_matches_list, tournament_match_links, match_count = [], {}, 0
        for link in tournament_links.values():
            matches_list, match_links = self._extract_tournament_matches(link, match_count)
            match_count = max(match_links.keys())
            tournament_matches_list.extend(matches_list)
            tournament_match_links.update(match_links)

        for link in tournament_match_links.values():
            print(MAIN_WEBSITE + link)


if __name__ == "__main__":
    cric_db = CricketDatabase()
    last_extracted_series = "Sri Lanka tour of India, 2020 "
    # last_extracted_series = None
    cric_db.run(last_extracted_series=last_extracted_series)
