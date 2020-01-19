class TOURNAMENT:
    tournament_type = 'TOURNAMENT_TYPE'
    tournament_title = 'TOURNAMENT_TITLE'
    tournament_year = 'TOURNAMENT_YEAR'
    tournament_start_month = 'TOURNAMENT_START_MONTH'
    tournament_end_month = 'TOURNAMENT_END_MONTH'
    tournament_link = 'TOURNAMENT_LINK'
    collection_json = {
        tournament_type: None,
        tournament_title: None,
        tournament_year: None,
        tournament_start_month: None,
        tournament_end_month: None,
        tournament_link: None
    }


class MATCH:
    match_title = 'MATCH_TITLE'
    match_start_date = 'MATCH_START_DATE'
    match_end_date = 'MATCH_END_DATE'
    match_place = 'MATCH_PLACE'
    match_result = 'MATCH_RESULT'
    match_time_gmt = 'MATCH_TIME_GMT'
    match_time_local = 'MATCH_TIME_LOCAL'
    match_link = 'MATCH_LINK'
    collection_json = {
        match_title: None,
        match_start_date: None,
        match_end_date: None,
        match_place: None,
        match_result: None,
        match_time_gmt: None,
        match_time_local: None,
        match_link: None
    }
