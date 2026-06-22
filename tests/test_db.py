import os
import pytest

from src.db import fetch_unprocessed_news, fetch_unprocessed_nse


py_test_mark = pytest.mark.skipif(
    "DATABASE_URL" not in os.environ,
    reason="DATABASE_URL not in environment",
)


def test_fetch_unprocessed_news():
    """
    Tests the news fetch function
    """
    news = fetch_unprocessed_news()
    assert len(news) > 5
    for n in news:
        assert not n.get['category'] == ['other'] and not n.get['ticker_tags']


def test_fetch_unprocessed_nse():
    """
    Tests the nse fetch function
    """
    nse = fetch_unprocessed_nse()
    assert len(nse) > 5

def test_upsert_insight():
    
