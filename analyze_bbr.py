import logging

from curl_cffi import requests
from lxml import html

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

HTTP_OK = 200
TIMEOUT_SECONDS = 30
BROWSER_IMPERSONATION = "chrome120"


def get_table_info(url):
    """
    Fetches a web page and prints summaries of HTML tables with IDs, including tables that are inside HTML comments.

    Prints the HTTP status code, response content length, a list of visible tables (ID and up to five header names), a list of tables found inside HTML comments (ID and up to five header names), and counts for each category. On error or non-200 responses, prints an error message.

    Parameters:
        url (str): The fully qualified URL to fetch and analyze.
    """
    logger.info("--- Analyzing %s ---", url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        # Use curl-cffi to mimic a real browser TLS fingerprint
        response = requests.get(
            url,
            headers=headers,
            impersonate=BROWSER_IMPERSONATION,
            timeout=TIMEOUT_SECONDS,
        )
        logger.info("Status Code: %d", response.status_code)
        if response.status_code != HTTP_OK:
            logger.error("Failed to fetch %s", url)
            return

        content = response.text
        logger.info("Content Length: %d", len(content))

        # Check for visible tables
        tree = html.fromstring(content)
        visible_tables = tree.xpath("//table[@id]")
        logger.info("Found %d visible tables with IDs.", len(visible_tables))
        for table in visible_tables:
            table_id = table.get("id")
            headers_list = [
                th.text_content().strip()
                for th in table.xpath(".//thead//th")
                if th.text_content().strip()
            ]
            logger.info(
                "  [Visible] ID: %s | Cols: %s...",
                table_id,
                ", ".join(headers_list[:5]),
            )

        # Check for commented tables
        # BBR comments out huge chunks of HTML, not just single tables
        comments = tree.xpath("//comment()")
        commented_table_count = 0
        for comment in comments:
            comment_text = comment.text
            if comment_text and "<table" in comment_text:
                # Some comments might contain multiple tables or partial HTML
                try:
                    # Clean up the comment text to be more parsable if it's just a fragment
                    if not comment_text.strip().startswith("<"):
                        # Try to find the first <table
                        start = comment_text.find("<table")
                        comment_text = comment_text[start:]

                    comment_tree = html.fromstring(comment_text)
                    tables = comment_tree.xpath("//table[@id]")
                    for table in tables:
                        table_id = table.get("id")
                        headers_list = [
                            th.text_content().strip()
                            for th in table.xpath(".//thead//th")
                            if th.text_content().strip()
                        ]
                        logger.info(
                            "  [Commented] ID: %s | Cols: %s...",
                            table_id,
                            ", ".join(headers_list[:5]),
                        )
                        commented_table_count += 1
                except Exception:
                    pass
        logger.info("Found %d tables in comments.", commented_table_count)

    except Exception:
        logger.exception("Error analyzing URLs")


urls = [
    "https://www.basketball-reference.com/players/j/jamesle01.html",
    "https://www.basketball-reference.com/teams/BOS/2024.html",
    "https://www.basketball-reference.com/boxscores/202406170BOS.html",
    "https://www.basketball-reference.com/leagues/NBA_2024_totals.html",
    "https://www.basketball-reference.com/leagues/NBA_2024.html",
]

for url in urls:
    get_table_info(url)
