from datetime import date

import pytest


@pytest.mark.skip(reason="Runs actual scraping and we don't want that.")
def test_scrape(john_doe_tw):
    tweets = john_doe_tw.scrape(
        flow="to",
        since=date(year=1970, month=1, day=1),
        until=date(year=2050, month=12, day=29),
        limit=42,
    )

    assert tweets
    assert isinstance(tweets, list)
    assert len(tweets) == 42


@pytest.mark.skip(reason="Runs HF pipeline and we don't want that.")
def test_sentiment(john_doe_tw, from_tweets):
    sentiments = john_doe_tw.sentiment(
        tweets=from_tweets, labels=["positive", "neutral", "negatve"]
    )

    assert sentiments
    assert isinstance(sentiments, dict)
    # TODO


@pytest.mark.skip(reason="Runs HF pipeline and we don't want that.")
def test_summary(john_doe_tw, from_tweets):
    summary = john_doe_tw.summarize(
        tweets=from_tweets,
    )

    assert summary
    assert isinstance(summary, str)
    # TODO


def test_fans(john_doe_tw, to_tweets):
    fans = john_doe_tw.fans(tweets=to_tweets)

    assert fans == ["JaneDoe", "ConcernedCitizen"]


def test_query(john_doe_tw):
    assert (
        john_doe_tw._generate_query(
            flow="to",
            since=date(year=1970, month=1, day=1),
            until=date(year=2050, month=12, day=31),
        )
        == "(to:JohnDoe) since:1970-01-01 until:2050-12-31"
    )

    assert (
        john_doe_tw._generate_query(
            flow="from",
            since=date(year=1970, month=1, day=1),
            until=date(year=2050, month=12, day=31),
        )
        == "(from:JohnDoe) since:1970-01-01 until:2050-12-31"
    )
