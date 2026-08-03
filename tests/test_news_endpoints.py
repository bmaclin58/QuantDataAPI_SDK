import unittest

from QuantDataAPI.errors import QuantDataClientError, QuantDataConfigurationError
from tests.endpoint_test_support import client_with_payload


NEWS_ARTICLES_PAGE = {
    "data": [
        {
            "id": 412057,
            "publishedTime": 1747137612000,
            "title": "Apple unveils new chip roadmap",
            "topics": ["PRODUCT_LAUNCHES"],
            "tickers": [
                {"ticker": "AAPL", "sentiment": "MODERATELY_BULLISH"}
            ],
            "body": "Article body",
        }
    ],
    "nextSearchAfter": ["1747137612000", "412057"],
}


class NewsArticlesTests(unittest.TestCase):
    def test_posts_exact_time_filter_request_and_preserves_json_page(self):
        client = client_with_payload(NEWS_ARTICLES_PAGE)
        result = client.get_news_articles(
            startTime="2026-05-13T13:30:00Z",
            endTime="2026-05-13T20:00:00Z",
            size=50,
            searchAfter=["1747137000000", "412000"],
            includes=["ID", "PUBLISHED_TIME", "TICKER", "TITLE"],
            includeBody=True,
            tickers=["AAPL", "NVDA"],
            topics=["EARNINGS_BEATS", "Product Launches"],
            sentiments=["MODERATELY_BULLISH"],
            filterExpression={"field": "publishedTime", "gte": 1747137000000},
        )
        self.assertEqual(result, NEWS_ARTICLES_PAGE)
        client._session.post.assert_called_once_with(
            "https://api.quantdata.us/v1/news/tool/news-articles",
            json={
                "timeRange": {
                    "startTime": "2026-05-13T13:30:00Z",
                    "endTime": "2026-05-13T20:00:00Z",
                },
                "size": 50,
                "searchAfter": ["1747137000000", "412000"],
                "includes": ["ID", "PUBLISHED_TIME", "TICKER", "TITLE"],
                "includeBody": True,
                "filter": {
                    "tickers": ["AAPL", "NVDA"],
                    "topics": ["EARNINGS_BEATS", "Product Launches"],
                    "sentiments": ["MODERATELY_BULLISH"],
                },
                "filterExpression": {
                    "field": "publishedTime",
                    "gte": 1747137000000,
                },
            },
            timeout=30,
        )

    def test_validates_time_range_page_size_and_response_shape(self):
        client = client_with_payload(NEWS_ARTICLES_PAGE)
        with self.assertRaisesRegex(ValueError, "both be provided"):
            client.get_news_articles(startTime="2026-05-13T13:30:00Z")
        with self.assertRaisesRegex(ValueError, "after startTime"):
            client.get_news_articles(
                startTime="2026-05-13T20:00:00Z",
                endTime="2026-05-13T13:30:00Z",
            )
        with self.assertRaisesRegex(ValueError, "ISO-8601 datetime"):
            client.get_news_articles(
                startTime="2026-05-13",
                endTime="2026-05-14",
            )
        with self.assertRaisesRegex(ValueError, "between 1 and 100"):
            client.get_news_articles(size=0)
        client._session.post.assert_not_called()

        for payload in ({"data": {}}, {"data": [], "nextSearchAfter": "bad"}):
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(
                    QuantDataClientError,
                    "news articles response",
                ):
                    client_with_payload(payload).get_news_articles()

    def test_accepts_omitted_or_null_cursor(self):
        for payload in ({"data": []}, {"data": [], "nextSearchAfter": None}):
            with self.subTest(payload=payload):
                self.assertEqual(
                    client_with_payload(payload).get_news_articles(),
                    payload,
                )

    def test_rejects_dataframe_output_before_transport(self):
        client = client_with_payload(NEWS_ARTICLES_PAGE, output_type="pandas")
        with self.assertRaisesRegex(
            QuantDataConfigurationError,
            "only supports JSON output",
        ):
            client.get_news_articles()
        client._session.post.assert_not_called()

    def test_rejects_non_projectable_body_and_sentiment_fields(self):
        client = client_with_payload(NEWS_ARTICLES_PAGE)
        for arguments in ({"includes": ["BODY"]}, {"excludes": ["SENTIMENT"]}):
            with self.subTest(arguments=arguments), self.assertRaisesRegex(
                ValueError,
                "not projectable",
            ):
                client.get_news_articles(**arguments)
        client._session.post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
