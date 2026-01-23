from unittest import TestCase
from unittest.mock import MagicMock, PropertyMock, patch

from src.scraper.html import SearchResult


class TestSearchResult(TestCase):
    def test_resource_link_query(self):
        assert SearchResult(html=MagicMock()).resource_link_query == './div[@class="search-item-name"]//a'

    @patch.object(SearchResult, "resource_link_query", new_callable=PropertyMock)
    def test_resource_link_when_no_matching_links(self, mocked_query):
        mocked_query.return_value = "some query"
        html = MagicMock()
        html.xpath = MagicMock(return_value=[])

        assert SearchResult(html=html).resource_link is None
        html.xpath.assert_called_once_with("some query")

    @patch.object(SearchResult, "resource_link_query", new_callable=PropertyMock)
    def test_resource_link_when_matching_links(self, mocked_query):
        mocked_query.return_value = "some query"
        first_link = MagicMock()
        html = MagicMock()
        html.xpath = MagicMock(return_value=[first_link])

        assert SearchResult(html=html).resource_link == first_link
        html.xpath.assert_called_once_with("some query")

    @patch.object(SearchResult, "resource_link", new_callable=PropertyMock)
    def test_resource_location_when_resource_link_is_none(self, mocked_resource_link):
        mocked_resource_link.return_value = None
        assert SearchResult(html=MagicMock()).resource_location is None

    @patch.object(SearchResult, "resource_link", new_callable=PropertyMock)
    def test_resource_location_when_resource_link_is_not_none(
        self, mocked_resource_link
    ):
        link = MagicMock()
        link.attrib = MagicMock()
        link.attrib.__getitem__ = MagicMock(return_value="some href")
        mocked_resource_link.return_value = link

        assert SearchResult(html=MagicMock()).resource_location == "some href"
        link.attrib.__getitem__.assert_called_once_with("href")

    @patch.object(SearchResult, "resource_link", new_callable=PropertyMock)
    def test_resource_name_when_resource_link_is_none(self, mocked_resource_link):
        mocked_resource_link.return_value = None
        assert SearchResult(html=MagicMock()).resource_name is None

    @patch.object(SearchResult, "resource_link", new_callable=PropertyMock)
    def test_resource_name_when_resource_link_is_not_none(self, mocked_resource_link):
        link = MagicMock()
        link.text_content = MagicMock(return_value="some content")
        mocked_resource_link.return_value = link
        assert SearchResult(html=MagicMock()).resource_name == "some content"
        link.text_content.assert_called_once_with()

    def test_different_class_is_not_equal(self):
        assert SearchResult(html=MagicMock()) != "jaebaebae"

    def test_different_html_but_same_class_is_not_equal(self):
        assert SearchResult(html=MagicMock()) != SearchResult(html=MagicMock())

    def test_same_html_and_same_class_is_equal(self):
        html = MagicMock()
        assert SearchResult(html=html) == SearchResult(html=html)
