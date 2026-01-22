from curl_cffi import requests
from lxml import html
import re

def get_table_info(url):
    print(f"\n--- Analyzing {url} ---")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    try:
        # Use curl-cffi to mimic a real browser TLS fingerprint
        response = requests.get(url, headers=headers, impersonate="chrome120", timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            return
            
        content = response.text
        print(f"Content Length: {len(content)}")
        
        # Check for visible tables
        tree = html.fromstring(content)
        visible_tables = tree.xpath('//table[@id]')
        print(f"Found {len(visible_tables)} visible tables with IDs.")
        for table in visible_tables:
            table_id = table.get('id')
            headers_list = [th.text_content().strip() for th in table.xpath('.//thead//th') if th.text_content().strip()]
            print(f"  [Visible] ID: {table_id} | Cols: {', '.join(headers_list[:5])}...")

        # Check for commented tables
        # BBR comments out huge chunks of HTML, not just single tables
        comments = tree.xpath('//comment()')
        commented_table_count = 0
        for comment in comments:
            comment_text = comment.text
            if comment_text and '<table' in comment_text:
                # Some comments might contain multiple tables or partial HTML
                try:
                    # Clean up the comment text to be more parsable if it's just a fragment
                    if not comment_text.strip().startswith('<'):
                        # Try to find the first <table
                        start = comment_text.find('<table')
                        comment_text = comment_text[start:]
                    
                    comment_tree = html.fromstring(comment_text)
                    tables = comment_tree.xpath('//table[@id]')
                    for table in tables:
                        table_id = table.get('id')
                        headers_list = [th.text_content().strip() for th in table.xpath('.//thead//th') if th.text_content().strip()]
                        print(f"  [Commented] ID: {table_id} | Cols: {', '.join(headers_list[:5])}...")
                        commented_table_count += 1
                except:
                    pass
        print(f"Found {commented_table_count} tables in comments.")

    except Exception as e:
        print(f"Error: {e}")

urls = [
    "https://www.basketball-reference.com/players/j/jamesle01.html",
    "https://www.basketball-reference.com/teams/BOS/2024.html",
    "https://www.basketball-reference.com/boxscores/202406170BOS.html",
    "https://www.basketball-reference.com/leagues/NBA_2024_totals.html",
    "https://www.basketball-reference.com/leagues/NBA_2024.html"
]

for url in urls:
    get_table_info(url)
