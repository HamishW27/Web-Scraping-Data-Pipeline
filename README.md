# Web-Scraping-Data-Pipeline

> This is a Web Scraper built with selenium and bs4. Its goal is to download information on the games in the Epic Games Store.  

## Milestone 1

- The Selenium webdriver is used to scrape the list of games that the Epic Games store provides. I wish to use this knowledge to find trends in genre over time as well as to track price changes. The scraper can be run inside of a docker container available at Docker Hub.

```python
class Scraper:
    def __init__(self, webpage) -> None:
        options = Options()
        options.headless = True
        self.webpage = webpage
        self.driver = webdriver.Chrome(options=options)
        self.links = []
```

## Milestone 2

- Now that the list of games has been scraped, BeautifulSoup is used to constrict a dictionary of useful information about each game. This is preferable to using Selenium as the data is contained in the html file of each game's page and therefore establishing a connection to each webpage is redundant and costs time. 

```python
@staticmethod
    def scrape_page_info(url, url_and_ids):
        '''
        This is a static method that scrapes the useful information 
        of an epicgames.com game's url

        Args: 
            url(string): the url that the user wishes to scrape.
            Though this is passed in via the method in main.

        Returns: 
            game_dict(dictionary): A dictionary of useful attributes.
            Namely the title; the current and previous
            prices with the discount, if applicable;
            critics review scores; the name of the developer;
            the name of the publisher; the game's release date; and a list of photo urls
        '''
```

## Milestone 3

- Used urllib and pandas to download images and json information and store them within the filesystem. Path was used to create appropriate directories.

```python
def create_folders(id):
    Path('./raw_data/' + id
             ).mkdir(parents=True, exist_ok=True)
    Path('./raw_data/' + id + '/images'
             ).mkdir(parents=True, exist_ok=True)
```

## Milestone 4

- Introduced a test.py file to run unit tests. These test that the functions return specific expected links or file types.

```python
def test_get_links(self):
        epicgames = Scraper(
        'https://www.epicgames.com/store/en-US/'
        'browse?sortBy=releaseDate&sortDir=DESC&count=1000')
        expected_item = 'https://www.epicgames.com/store/en-US/p/grand-theft-auto-v'
        actual_items = epicgames.get_links()
        self.assertIn(expected_item, actual_items)
```

## Milestone 5 

- Added methods to scalably store data using AWS. Files detailing information about images and games are uploaded to RDS and actual files are backed up to S3. Tables are constructed using SQLAlchemy and pandas dataframes. 