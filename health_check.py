import pytz
from datetime import datetime, timedelta
from src.db import (
    fetch_oldest_unprocessed_news, fetch_oldest_unprocessed_nse,
    fetch_last_inserted_insight, get_urgency_score_pct
)

tz= pytz.timezone('Asia/Kolkata')
NOW = tz.localize(datetime.now())

PASS = '✅ PASS'
FAIL = '❌ FAIL'


def check_last_unprocessed():
    """
    Checks whether the oldest unprocessed data is not older than 2 hours
    """
    print("\n-----Check oldest unprocessed data----")
    news = fetch_oldest_unprocessed_news()
    delta = NOW-news.get('ingested_at')
    if delta < timedelta(hours=2):
        print(f'{PASS}  oldest unprocessed news @{delta}')
    else:
        print(f'{FAIL} unprocesssed news @{delta}')
    nse = fetch_oldest_unprocessed_nse()
    delta = NOW-nse.get('ingested_at')
    if delta < timedelta(hours=2):
        print(f'{PASS}  oldest unprocessed nse filing  @{delta}')
    else:
        print(f'{FAIL} unprocesssed nse filing @{delta}')


def check_last_inserted_insight():
    """
    Checks whether last inserted row insight is inserted under 30 minutes
    """
    print('\n------CHECK LAST INSERTED INSIGHT------')
    insight = fetch_last_inserted_insight()
    delta = NOW-insight.get('processed_at')
    if delta < timedelta(minutes=30):
        print(f'{PASS} last inserted insight row @{delta}')
    else:
        print(f'{FAIL} last inserted insight row @{delta}')


def check_urgency_distribution():
    """
        Checks for the urgency score distribution in past 24 hours
    """
    print('\n-----CHECKS URGENCY SCORE DICTRIBUTION------')
    for i in range(1, 6):
        pct = get_urgency_score_pct(i)
        if pct and pct > 4.0:
            print(f'{PASS} urgency score {i} has percentage = {pct}')
        else:
            print(f'{FAIL} urgency score {i} has percentage= {pct}')


if __name__ == '__main__':
    all_ok = all([
        check_last_inserted_insight(),
        check_last_unprocessed(),
        check_urgency_distribution()
    ])

    if all_ok:
        print(f'{PASS} all checks are passed')
    else:
        print(f'{FAIL} Some checks are failing, correct them')
