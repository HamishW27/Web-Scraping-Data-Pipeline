from project import *
import unittest


class TestLinks(unittest.TestCase):

    def test_get_links(self):
        epicgames = Scraper(
        'https://www.epicgames.com/store/en-US/'
        'browse?sortBy=releaseDate&sortDir=DESC&count=1000')
        expected_item = 'https://www.epicgames.com/store/en-US/p/grand-theft-auto-v'
        actual_items = epicgames.get_links()
        self.assertIn(expected_item, actual_items)
    
    def test_scrape_page_info(self):
        id_links = [{'url': 'https://www.epicgames.com/store/en-US/p/grand-theft-auto-v', 'id': '7c886093-e7e4-4e22-86c7-182183fdb925'}]
        url = 'https://www.epicgames.com/store/en-US/p/grand-theft-auto-v'
        actual_items = Scraper.scrape_page_info(url, id_links)
        self.assertEqual('Grand Theft Auto V', actual_items['title'])
    
    def test_parse_percentage(self):
        self.assertEqual(parse_percentage('90%'), 90, 'Should be an integer 90')

    def test_flatten(self):
        example_list = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        flattened_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.assertEqual(flatten(example_list), flattened_list)
    
    def test_find_existing_table(self):
        url_table = find_existing_table('games','url')
        self.assertIsInstance(url_table, list)
    
    def test_read_into_table(self):
        json_file = "raw_data/*/*.json"
        expected_file = read_into_table(json_file)
        self.assertIsInstance(expected_file, pd.DataFrame)

if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=0, exit=False)