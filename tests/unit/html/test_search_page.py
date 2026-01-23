from unittest import TestCase
from unittest.mock import MagicMock, PropertyMock, patch

from src.scraper.html import PlayerSearchResult, SearchPage


class TestSearchPage(TestCase):
    def test_nba_aba_baa_players_content_query(self):
        assert (
            SearchPage(html=MagicMock()).nba_aba_baa_players_content_query
            == '//div[@id="searches"]/div[@id="players"]'
        )

    @patch.object(
        SearchPage, "nba_aba_baa_players_content_query", new_callable=PropertyMock
    )
    def test_nba_aba_baa_players_pagination_links_query(self, mocked_query):
        mocked_query.return_value = "some query"

        assert (
            SearchPage(html=MagicMock()).nba_aba_baa_players_pagination_links_query
            == 'some query/div[@class="search-pagination"]/a'
        )

    @patch.object(
        SearchPage, "nba_aba_baa_players_content_query", new_callable=PropertyMock
    )
    def test_nba_aba_baa_player_search_items_query(self, mocked_query):
        mocked_query.return_value = "some query"

        assert (
            SearchPage(html=MagicMock()).nba_aba_baa_player_search_items_query
            == 'some query/div[@class="search-item"]'
        )

    @patch.object(
        SearchPage,
        "nba_aba_baa_players_pagination_links_query",
        new_callable=PropertyMock,
    )
    def test_nba_aba_baa_players_pagination_links(self, mocked_query):
        mocked_query.return_value = "some query"
        html = MagicMock()
        links = [MagicMock(return_value="some"), MagicMock(return_value="links")]
        html.xpath = MagicMock(return_value=links)

        assert SearchPage(html=html).nba_aba_baa_players_pagination_links == links
        html.xpath.asset_called_once_with("some query")

    @patch.object(
        SearchPage, "nba_aba_baa_players_pagination_links", new_callable=PropertyMock
    )
    def test_nba_aba_baa_players_pagination_url_is_none_when_no_pagination_links(
        self, mocked_links
    ):
        mocked_links.return_value = []
        assert SearchPage(html=MagicMock()).nba_aba_baa_players_pagination_url is None

    @patch.object(
        SearchPage, "nba_aba_baa_players_pagination_links", new_callable=PropertyMock
    )
    def test_nba_aba_baa_players_pagination_url_is_first_link_href_attrib_when_single_link_is_not_at_end_of_results(
        self, mocked_links
    ):
        link = MagicMock()
        link.text_content = MagicMock(return_value="jaebaebae")
        link.attrib = MagicMock()
        link.attrib.__getitem__ = MagicMock(return_value="some text content")
        mocked_links.return_value = [link]

        assert (
            SearchPage(html=MagicMock()).nba_aba_baa_players_pagination_url
            == "some text content"
        )
        link.attrib.__getitem__.assert_called_once_with("href")

    @patch.object(
        SearchPage, "nba_aba_baa_players_pagination_links", new_callable=PropertyMock
    )
    def test_nba_aba_baa_players_pagination_url_is_none_when_single_link_is_at_end_of_results(
        self, mocked_links
    ):
        link = MagicMock()
        link.text_content = MagicMock(return_value="Previous 100 Results")
        mocked_links.return_value = [link]

        assert SearchPage(html=MagicMock()).nba_aba_baa_players_pagination_url is None
        link.text_content.assert_called_once_with()

    @patch.object(
        SearchPage, "nba_aba_baa_players_pagination_links", new_callable=PropertyMock
    )
    def test_nba_aba_baa_players_pagination_url_is_second_link_href_attrib_when_multiple_links(
        self, mocked_links
    ):
        first_link = MagicMock()
        first_link.attrib = MagicMock()
        first_link.attrib.__getitem__ = MagicMock(return_value="some text content")

        second_link = MagicMock()
        second_link.attrib = MagicMock()
        second_link.attrib.__getitem__ = MagicMock(
            return_value="some other text content"
        )
        mocked_links.return_value = [first_link, second_link]

        assert (
            SearchPage(html=MagicMock()).nba_aba_baa_players_pagination_url
            == "some other text content"
        )
        second_link.attrib.__getitem__.assert_called_once_with("href")

    @patch.object(
        SearchPage, "nba_aba_baa_player_search_items_query", new_callable=PropertyMock
    )
    def test_nba_aba_baa_players(self, mocked_query):
        mocked_query.return_value = "some query"

        first_result = MagicMock(name="first html result")
        second_result = MagicMock(name="second html result")
        third_result = MagicMock(name="third html result")

        html = MagicMock()
        html.xpath = MagicMock(return_value=[first_result, second_result, third_result])

        assert SearchPage(html=html).nba_aba_baa_players == [
            PlayerSearchResult(html=first_result),
            PlayerSearchResult(html=second_result),
            PlayerSearchResult(html=third_result),
        ]
