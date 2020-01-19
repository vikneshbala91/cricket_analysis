import requests
from bs4 import BeautifulSoup
import datetime
from src.config import BASE_URL, MAIN_WEBSITE, MIN_SERIES_YEAR
from src.collection_schema import TOURNAMENT


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
        year = int(datetime.datetime.now().year)

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
                    print(collection_json[TOURNAMENT.tournament_title])
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

    def run(self, last_extracted_series):
        tournament_data_list, tournament_links = self._extract_tournament(last_extracted_series=last_extracted_series)
        for l in tournament_links.values():
            print(MAIN_WEBSITE + l)


if __name__ == "__main__":
    cric_db = CricketDatabase()
    # last_extracted_series = "Ireland tour of West Indies, 2020"
    last_extracted_series = None
    cric_db.run(last_extracted_series=last_extracted_series)
