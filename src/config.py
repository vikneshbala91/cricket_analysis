import datetime
MAIN_WEBSITE = "https://www.cricbuzz.com"
BASE_URL = "https://www.cricbuzz.com/cricket-scorecard-archives/"
MIN_SERIES_YEAR = 2018
RETRY_SECONDS = 10
MAX_RETRY_COUNT = 1

encode_month = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12
}


def _date(date_month_string, year):
    date = int(date_month_string.split(' ')[1])
    month = int(encode_month[date_month_string.split(' ')[0]])
    return datetime.date(year, month, date)
