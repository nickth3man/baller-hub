"""HTML wrappers for search result pages."""


class SearchPage:
    """Wraps the Search Results page (e.g., /search/search.fcgi?search=LeBron).

    Attributes:
        html (lxml.html.HtmlElement): The raw HTML element for the page.
    """

    def __init__(self, html):
        """Initialize the page wrapper.

        Args:
            html (lxml.html.HtmlElement): The raw HTML element for the page.
        """
        self.html = html

    @property
    def nba_aba_baa_players_content_query(self):
        """str: XPath query for the players results section."""
        return '//div[@id="searches"]/div[@id="players"]'

    @property
    def nba_aba_baa_players_pagination_links_query(self):
        """str: XPath query for pagination links within player results."""
        return f'{self.nba_aba_baa_players_content_query}/div[@class="search-pagination"]/a'

    @property
    def nba_aba_baa_player_search_items_query(self):
        """str: XPath query for individual player result items."""
        return f'{self.nba_aba_baa_players_content_query}/div[@class="search-item"]'

    @property
    def nba_aba_baa_players_pagination_links(self):
        """list[lxml.html.HtmlElement]: List of pagination link elements."""
        return self.html.xpath(self.nba_aba_baa_players_pagination_links_query)

    @property
    def nba_aba_baa_players_pagination_url(self):
        """str | None: URL for the next page of results, if any."""
        links = self.nba_aba_baa_players_pagination_links

        if len(links) <= 0:
            return None

        first_link = links[0]

        if len(links) == 1:
            if first_link.text_content() == "Previous 100 Results":
                return None

            return first_link.attrib["href"]

        return links[1].attrib["href"]

    @property
    def nba_aba_baa_players(self):
        """list[PlayerSearchResult]: List of player results found."""
        return [
            PlayerSearchResult(html=result_html)
            for result_html in self.html.xpath(
                self.nba_aba_baa_player_search_items_query
            )
        ]


class SearchResult:
    """Base class for a single item in search results.

    Attributes:
        html (lxml.html.HtmlElement): The raw HTML element for the result item.
    """

    def __init__(self, html):
        """Initialize the result item wrapper.

        Args:
            html (lxml.html.HtmlElement): The raw HTML element for the result item.
        """
        self.html = html

    @property
    def resource_link_query(self):
        """str: XPath query for the main link to the resource."""
        return './div[@class="search-item-name"]//a'

    @property
    def resource_link(self):
        """lxml.html.HtmlElement | None: The link element."""
        links = self.html.xpath(self.resource_link_query)

        if len(links) > 0:
            return links[0]

        return None

    @property
    def resource_location(self):
        """str | None: The URL path to the resource (e.g. /players/j/jamesle01.html)."""
        link = self.resource_link

        if link is None:
            return None

        return link.attrib["href"]

    @property
    def resource_name(self):
        """str | None: Display name of the resource."""
        link = self.resource_link

        if link is None:
            return None

        return link.text_content()

    def __eq__(self, other):
        """Check if two results represent the same HTML element.

        Args:
            other (object): The other object to compare.

        Returns:
            bool: True if the results wrap the same HTML element, False otherwise.
        """
        if isinstance(other, SearchResult):
            return self.html == other.html
        return False


class PlayerSearchResult(SearchResult):
    """Wraps a search result specifically for a player.

    Attributes:
        html (lxml.html.HtmlElement): The raw HTML element for the result item.
    """

    @property
    def league_abbreviation_query(self):
        """str: XPath query for league info."""
        return './div[@class="search-item-league"]'

    @property
    def league_abbreviations(self):
        """str | None: Leagues associated with the player (e.g. 'NBA')."""
        abbreviations = self.html.xpath(self.league_abbreviation_query)

        if len(abbreviations) > 0:
            return abbreviations[0].text_content()

        return None
