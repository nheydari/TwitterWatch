import pytest

from TwitterWatch import TwitterWatch


@pytest.fixture(scope="session")
def john_doe_tw() -> TwitterWatch:
    return TwitterWatch("JohnDoe")


@pytest.fixture(scope="session")
def from_tweets():
    return [
        TwitterWatch.TweetType(
            date="1970-01-01", tweet="I am very opinionated.", username="JohnDoe"
        ),
        TwitterWatch.TweetType(
            date="2050-12-31",
            tweet="And all the world must know about it.",
            username="JohnDoe",
        ),
    ]


@pytest.fixture(scope="session")
def to_tweets():
    return [
        TwitterWatch.TweetType(date="1970-01-01", tweet="Booo.", username="JaneDoe"),
        TwitterWatch.TweetType(
            date="2010-06-15", tweet="Are you alive?", username="ConcernedCitizen"
        ),
        TwitterWatch.TweetType(
            date="2050-12-31",
            tweet="Your opinions suck and you should feel bad.",
            username="JaneDoe",
        ),
    ]
