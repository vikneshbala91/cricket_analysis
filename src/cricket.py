import requests, time
from bs4 import BeautifulSoup
from datetime import datetime, date
from src.config import BASE_URL, MAIN_WEBSITE, _date, RETRY_SECONDS, MAX_RETRY_COUNT
from src.collection_schema import TOURNAMENT, MATCH


class CricketDatabase:
    def __init__(self):
        print("Cricket database sourced from cricbuzz")

    def _extract_tournament(self, last_extraction_date=None, only_series=None, start_year=None):
        """
        :param LAST_SERIES:
        :return:
        """
        if only_series is not None:
            only_series_found = False
            last_extraction_year = int(datetime.today().year) + 1
        elif last_extracted_date is not None:
            only_series_found = True
            last_extraction_date = last_extraction_date
            try:
                last_extraction_date = datetime.strptime(last_extraction_date, '%Y-%m-%d').date()
                last_extraction_year = last_extraction_date.year
            except IOError:
                raise Exception('last extraction date format is wrong, please give in YYYY-MM-DD format')
        else:
            last_extraction_year = None
            only_series_found = None

        tournament_data_list, tournament_links, tournament_count = [], {}, 0
        year = int(datetime.today().year) if start_year is None else start_year

        while year >= last_extraction_year or not only_series_found:
            print('extracting tournaments of {}'.format(year))
            page = requests.get(BASE_URL + str(year))
            main_soup = BeautifulSoup(page.content, 'html.parser')
            tour_level = main_soup.findAll('h2', attrs={"class": "cb-lv-scr-mtch-hdr"})
            tour_level = [t.text for t in tour_level]
            tour_information = main_soup.findAll('div', attrs={"class": "cb-col-84"})
            for tour_type, tour_info in zip(tour_level, tour_information):
                for tour in tour_info.children:
                    collection_json = {}
                    date_object = [x.strip() for x in tour.contents[1].text.strip().split('-')]
                    start_date = _date(date_object[0], year)
                    end_date = _date(date_object[1], year)
                    if end_date.month < start_date.month:
                        end_date = date(year + 1, end_date.month, end_date.day)
                    if end_date > date.today():
                        continue
                    if last_extraction_date is not None and start_date > last_extraction_date:
                        continue
                    collection_json[TOURNAMENT.tournament_type] = tour_type
                    collection_json[TOURNAMENT.tournament_title] = tour.contents[0].text.strip()
                    collection_json[TOURNAMENT.tournament_year] = year
                    collection_json[TOURNAMENT.tournament_start_date] = start_date
                    collection_json[TOURNAMENT.tournament_end_date] = end_date
                    collection_json[TOURNAMENT.tournament_link] = tour.contents[0]['href']
                    tournament_count += 1
                    if last_extraction_date is not None:
                        tournament_data_list.append(collection_json)
                        tournament_links.update({tournament_count: collection_json[TOURNAMENT.tournament_link]})
                    elif only_series is not None:
                        if tour.contents[0].text.strip() == only_series.strip():
                            tournament_data_list.append(collection_json)
                            tournament_links.update({1: collection_json[TOURNAMENT.tournament_link]})
                            only_series_found = True
            year = year - 1
        return tournament_data_list, tournament_links

    def _extract_tournament_matches(self, tournament_link, match_count):
        print("TOUR: ", MAIN_WEBSITE + tournament_link)
        page = requests.get(MAIN_WEBSITE + tournament_link)
        main_soup = BeautifulSoup(page.content, 'html.parser')
        match_details = main_soup.findAll('div', attrs={"class": "cb-series-matches"})
        retry_seconds, retry_counter = RETRY_SECONDS, 1
        while len(match_details) == 0:
            time.sleep(retry_seconds)
            print('match_details re-trying.. ({})'.format(retry_counter))
            page = requests.get(MAIN_WEBSITE + tournament_link)
            main_soup = BeautifulSoup(page.content, 'html.parser')
            match_details = main_soup.findAll('div', attrs={"class": "cb-series-matches"})
            retry_seconds = retry_seconds + RETRY_SECONDS * retry_counter
            retry_counter += 1
            if retry_counter > MAX_RETRY_COUNT:
                print("skipping tournament after MAX retries")
                return None, None
        tournament_matches_list, tournament_match_links = [], {}
        for match_box in match_details:
            collection_json = {}
            match_box_1 = match_box.findAll('div', attrs={"class": "schedule-date"})
            match_start_date, match_end_date = None, None
            for xx in match_box_1:
                try:
                    match_start_end_date = [str(datetime.fromtimestamp(int(x['ng-bind'].split('|')[0].strip()[:-3]))).
                                                split(" ")[0] for x in xx.findAll('span')]
                    match_start_date = match_start_end_date[0]
                    match_end_date = match_start_end_date[1] if len(match_start_end_date) == 2 else \
                        match_start_end_date[0]
                except:
                    match_start_date = match_start_date
                    match_end_date = match_end_date
            match_box_2 = match_box.find('div', attrs={"class": "cb-col-60"}).contents
            if match_box.find('a', attrs={"class": "cb-text-inprogress"}) is not None:
                match_result = match_box.find('a', attrs={"class": "cb-text-inprogress"}).text
            elif match_box.find('a', attrs={"class": "cb-text-complete"}) is not None:
                match_result = match_box.find('a', attrs={"class": "cb-text-complete"}).text
            else:
                match_result = None
            match_box_3 = match_box.find('div', attrs={"class": "cb-font-12"}).contents
            if 'href' not in str(match_box_2[0]):
                continue
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

    def _validate_input(self, last_extracted_date, only_series, start_year):

        if all([last_extracted_date, only_series, start_year]) is None:
            raise Exception("ALL EXPECTED INPUTS CAN'T BE NONE")
        elif last_extracted_date is None:
            if type(only_series) == str and len(only_series) > 0:
                pass
            else:
                raise Exception("only_series input not supported or wrongly provided")
        elif only_series is None:
            if start_year is not None:
                if type(start_year) == int and len(str(start_year)) == 4:
                    pass
                else:
                    raise Exception("start year - wrong input, please provide proper 4 digit year")
            try:
                datetime.strptime(last_extracted_date, '%Y-%m-%d').date()
            except IOError:
                raise Exception("Unsupported date format, please provide in YYYY-MM-DD")
        else:
            pass

    def run(self, last_extracted_date, only_series, start_year):

        if only_series is not None:
            last_extracted_date = None
            start_year = None
        elif last_extracted_date is not None:
            only_series = None
        else:
            pass

        self._validate_input(last_extracted_date, only_series, start_year)
        tournament_data_list, tournament_links = self._extract_tournament(last_extraction_date=last_extracted_date,
                                                                          only_series=only_series,
                                                                          start_year=start_year)
        tournament_matches_list, tournament_match_links, match_count, error_tournaments = [], {}, 0, []
        for link in tournament_links.values():
            matches_list, match_links = self._extract_tournament_matches(link, match_count)
            if matches_list is not None and match_links is not None:
                match_count = max(match_links.keys())
                tournament_matches_list.extend(matches_list)
                tournament_match_links.update(match_links)
            else:
                error_tournaments.append(link)

        for link in tournament_match_links.values():
            print(MAIN_WEBSITE + link)

        base_file_name = 'EXTRACT_' + str(start_year) + '_run_date_' + str(datetime.today().date())
        error_base_file_name = 'ERROR_' + str(start_year) + '_run_date_' + str(datetime.today().date())
        tour_file = base_file_name + '_tour_list.txt'
        tour_match_file = base_file_name + '_tour_match_list.txt'
        tour_match_details_file = base_file_name + 'tour_match_details.txt'
        error_tour_match_file = error_base_file_name + '_tour_match_list.txt'
        error_tour_match_details_file = error_base_file_name + 'tour_match_details.txt'

        with open(tour_file, 'w') as f:
            for item in tournament_data_list:
                f.write("%s\n" % item)

        with open(tour_match_file, 'w') as f:
            for item in tournament_matches_list:
                f.write("%s\n" % item)

        with open(error_tour_match_file, 'w') as f:
            for item in error_tournaments:
                f.write("%s\n" % item)


if __name__ == "__main__":
    cric_db = CricketDatabase()
    # last_extracted_date = str(date.today())
    year = 2020
    while year > 1889:
        start_year = year
        last_extracted_date = str(start_year) + '-12-31'
        only_series = None
        # only_series = 'Sri Lanka tour of Zimbabwe, 2020'
        # last_extracted_date = None
        cric_db.run(last_extracted_date=last_extracted_date, only_series=only_series, start_year=start_year)
        year = year - 1
