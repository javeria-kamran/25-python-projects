import requests
from bs4 import BeautifulSoup
import csv
import os
import time
from urllib.parse import urljoin, urlparse
from datetime import datetime
import json
import argparse
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, base_url: str, max_depth: int = 1, delay: float = 1.0):
        """
        Initialize the web scraper with configuration options.
        
        Args:
            base_url: The starting URL for scraping
            max_depth: Maximum depth to follow links (0 = only base URL)
            delay: Delay between requests in seconds
        """
        self.base_url = base_url
        self.max_depth = max_depth
        self.delay = delay
        self.visited_urls = set()
        self.domain = urlparse(base_url).netloc
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def is_valid_url(self, url: str) -> bool:
        """Check if a URL should be scraped."""
        parsed = urlparse(url)
        return (
            parsed.scheme in ('http', 'https') and
            parsed.netloc == self.domain and
            url not in self.visited_urls
        )

    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page with error handling."""
        try:
            time.sleep(self.delay)  # Respectful crawling
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                logger.warning(f"Skipping non-HTML content: {content_type}")
                return None
                
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def extract_data(self, soup: BeautifulSoup, url: str) -> Dict[str, List[Dict]]:
        """Extract structured data from a BeautifulSoup object."""
        data = {
            'metadata': {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'title': soup.title.string if soup.title else None
            },
            'headings': [],
            'links': [],
            'paragraphs': [],
            'images': [],
            'tables': []
        }

        # Extract headings
        for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
            data['headings'].append({
                'level': heading.name,
                'text': heading.get_text(strip=True),
                'id': heading.get('id')
            })

        # Extract links
        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(url, link['href'])
            if self.is_valid_url(absolute_url):
                data['links'].append({
                    'text': link.get_text(strip=True),
                    'url': absolute_url,
                    'is_external': urlparse(absolute_url).netloc != self.domain
                })

        # Extract paragraphs
        for para in soup.find_all('p'):
            text = para.get_text(strip=True)
            if text:  # Skip empty paragraphs
                data['paragraphs'].append({
                    'text': text,
                    'class': ' '.join(para.get('class', []))
                })

        # Extract images
        for img in soup.find_all('img'):
            data['images'].append({
                'src': urljoin(url, img.get('src', '')),
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })

        # Extract tables
        for table in soup.find_all('table'):
            rows = []
            for row in table.find_all('tr'):
                cells = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
                rows.append(cells)
            if rows:
                data['tables'].append({
                    'rows': rows,
                    'class': ' '.join(table.get('class', []))
                })

        return data

    def scrape_page(self, url: str, depth: int = 0) -> List[Dict]:
        """Recursively scrape a page and its links."""
        if depth > self.max_depth or not self.is_valid_url(url):
            return []

        self.visited_urls.add(url)
        soup = self.get_page_content(url)
        if not soup:
            return []

        page_data = self.extract_data(soup, url)
        results = [page_data]

        # Follow links if we haven't reached max depth
        if depth < self.max_depth:
            for link in page_data['links']:
                if not link['is_external']:
                    results.extend(self.scrape_page(link['url'], depth + 1))

        return results

    def save_results(self, data: List[Dict], format: str = 'csv') -> None:
        """Save scraped data in the specified format."""
        if not data:
            logger.warning("No data to save")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"scraped_data_{timestamp}.{format}"
        
        try:
            if format == 'csv':
                self._save_csv(data, filename)
            elif format == 'json':
                self._save_json(data, filename)
            else:
                logger.error(f"Unsupported format: {format}")
                return
                
            logger.info(f"Successfully saved results to {filename}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")

    def _save_csv(self, data: List[Dict], filename: str) -> None:
        """Save data to CSV file with separate sheets for each data type."""
        os.makedirs('output', exist_ok=True)
        full_path = os.path.join('output', filename)
        
        # Flatten the data structure for CSV
        flat_data = []
        for page in data:
            for data_type in ['headings', 'links', 'paragraphs', 'images', 'tables']:
                for item in page.get(data_type, []):
                    record = {
                        'page_url': page['metadata']['url'],
                        'page_title': page['metadata']['title'],
                        'data_type': data_type,
                        **item
                    }
                    flat_data.append(record)

        if not flat_data:
            logger.warning("No data to write to CSV")
            return

        with open(full_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
            writer.writeheader()
            writer.writerows(flat_data)

    def _save_json(self, data: List[Dict], filename: str) -> None:
        """Save data to JSON file."""
        os.makedirs('output', exist_ok=True)
        full_path = os.path.join('output', filename)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    """Command-line interface for the web scraper."""
    parser = argparse.ArgumentParser(description='Advanced Web Scraper')
    parser.add_argument('url', help='URL to scrape')
    parser.add_argument('-d', '--depth', type=int, default=1, 
                       help='Maximum depth to follow links (default: 1)')
    parser.add_argument('-f', '--format', choices=['csv', 'json'], default='csv',
                       help='Output format (default: csv)')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--log', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level (default: INFO)')
    
    args = parser.parse_args()
    
    # Set logging level
    logger.setLevel(args.log)
    
    try:
        logger.info(f"Starting scrape of {args.url} with depth {args.depth}")
        scraper = WebScraper(
            base_url=args.url,
            max_depth=args.depth,
            delay=args.delay
        )
        
        data = scraper.scrape_page(args.url)
        scraper.save_results(data, format=args.format)
        
        logger.info(f"Scraping completed. Visited {len(scraper.visited_urls)} pages.")
    except Exception as e:
        logger.error(f"Fatal error during scraping: {str(e)}")
        raise

if __name__ == "__main__":
    main()