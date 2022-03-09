# Web-Scraping-Data-Pipeline

> This is a Web Scraper built with selenium and bs4. Its goal is to download information on the games in the Epicgames Store.  

## Milestone 1

- The Selenium webdriver is used to scrape the list of games that the Epicgames store provides. I wish to use this knowledge to find trends in genre over time as well as to track price changes. The scraper can be run inside of a docker container available at Dockerhub.

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

- Now that the list of games has been scraped, BeautifulSoup is used to constrict a dictionary of useful infomration about each game. This is preferable to using Selenium as the data is contained in the html file of each game's page and therefore establishing a connection to each webpage is redundant and costs time. 

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