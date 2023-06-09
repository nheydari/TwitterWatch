from collections import defaultdict, namedtuple
from datetime import date
from functools import cache
from itertools import islice
from typing import Callable, DefaultDict, Iterable, Literal, Optional, Union

import snscrape.modules.twitter as sntwitter
from more_itertools import batched
from transformers import pipeline


class TwitterWatch:
    """Scraper, sentiment analysis and summarizer for Twitter

    Attributes:
        handle: Twitter handle of the target account.
        classifier: HuggingFace classifier of choice for sentiment analysis.
        summarizer: HuggingFace summarizer of choice.
        device: Hardware select by index.
    """

    TweetType = namedtuple("TweetType", ["date", "username", "tweet"])

    def __init__(
        self,
        handle: str,
        *,
        classifier: str = "zero-shot-classification",
        summarizer: str = "t5-large",
        device: int = 0,
    ):
        """Initializes the class Twitter watch with handle, classifier, summarizer, and device."""
        self.handle = handle
        self._classifier = classifier
        self._summarizer = summarizer
        self._device = device

    @property
    def classifier(
        self,
    ) -> Callable[
        [Iterable[str], list[str]], list[dict[str, Union[str, list[str], list[float]]]]
    ]:
        return pipeline(self._classifier, device=self._device)  # type: ignore

    @property
    def summarizer(self) -> Callable[[str, int, int], str]:
        return pipeline("summarization", model=self._summarizer)  # type: ignore

    def _generate_query(
        self,
        flow: Literal["to", "from"],
        since: date,
        until: date,
    ) -> str:
        """Generate a query string for Twitter API v2 search through snscrape.

        Args:
            flow: Literal string to select tweets `from` handle, or `to` handle.
            since: Limit by starting date.
            until: Limit by end date.

        Returns:
            Query string
        """
        return f"({flow}:{self.handle}) since:{since.isoformat()} until:{until.isoformat()}"

    @cache
    def scrape(
        self,
        flow: Literal["to", "from"],
        since: date,
        until: date,
        limit: Optional[int] = None,
    ) -> list[TweetType]:
        """Scrapes the account for tweets.

        Args:
            flow: Literal string to select tweets `from` handle, or `to` handle.
            since: Limit by starting date.
            until: Limit by end date.
            limit: Limit by number of tweets.

        Returns:
            List of tweets that match the query criteria.
        """
        return [
            *islice(
                (
                    self.TweetType(
                        date=tweet.date,
                        username=tweet.user.username,
                        tweet=tweet.content,
                    )
                    for tweet in sntwitter.TwitterSearchScraper(
                        self._generate_query(flow, since, until)
                    ).get_items()
                ),
                limit,
            )
        ]

    def sentiment(
        self, tweets: list[TweetType], labels: list[str]
    ) -> DefaultDict[str, float]:
        """
        Run sentiment analysis on provided tweets and labels.

        Args:
            tweets: List of tweets, as generated by scrape.
            labels: List of sentiment labels.

        Returns:
            Dictionary of average score per label
        """
        sentiments: DefaultDict[str, float] = defaultdict(float)
        sentiment_analysis = self.classifier([*map(lambda tweet: tweet.tweet, tweets)], labels)  # type: ignore

        for idx, item in enumerate(sentiment_analysis, start=1):
            for sentiment, score in zip(item["labels"], item["scores"]):
                sentiments[sentiment] = (sentiments[sentiment] * (idx - 1) + score) / idx  # type: ignore

        return sentiments

    def summarize(self, tweets: list[TweetType]) -> list[str]:
        """Summarize the tweets.

        Args:
            tweets: List of tweets, as generated by scrape.

        Returns:
            summary of tweets.
        """

        def _summarize(tweets: list[str]) -> list[str]:
            if len(tweets) > 1:
                return _summarize(
                    [
                        *map(
                            lambda batch: self.summarizer(  # type: ignore
                                batch, max_length=400, min_length=50
                            ),
                            [*map(" ".join, batched(tweets, 40))],
                        )
                    ]
                )
            else:
                return tweets

        return _summarize([*map(lambda tweet: tweet.tweet, tweets)])  # type: ignore

    @staticmethod
    def fans(tweets: list[TweetType]) -> list[str]:
        """Finds the fans of the handle.

        Args:
            tweets (list[TweetType]): List of tweets, as generated by scrape.

        Returns:
            List of handles sorted by number of @s
        """
        # int() = 0
        followers: DefaultDict[str, int] = defaultdict(int)

        for tweet in tweets:
            followers[tweet.username] += 1

        return sorted(followers, reverse=True)
