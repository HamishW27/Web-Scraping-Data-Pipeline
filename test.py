from project import Scraper
from project import parse_percentage
import unittest


class TestLinks(unittest.TestCase):

    def test_links(self):
        epicgames = Scraper(
        'https://www.epicgames.com/store/en-US/'
        'browse?sortBy=releaseDate&sortDir=DESC&count=1000')
        expected_item = 'https://www.epicgames.com/store/en-US/p/grand-theft-auto-v'
        actual_items = epicgames.get_links()
        self.assertIn(expected_item, actual_items)
    
    def test_scrape_page_info(self):
        url = 'https://www.epicgames.com/store/en-US/p/grand-theft-auto-v'
        actual_items = Scraper.scrape_page_info(url)
        self.assertEqual('Grand Theft Auto V', actual_items['title'])
    
    def test_parse_percentage(self):
        self.assertEqual(parse_percentage('90%'), 90, 'Should be an integer 90')

if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=0, exit=False)