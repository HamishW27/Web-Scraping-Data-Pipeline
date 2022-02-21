'''
This is a scraper module specifically for use with the website
"https://www.epicgames.com/store/en-US/."
it contains the Scraper class which allows you to:
- Scrape the homepage for links to games
- Scrape details about each game from their respective pages
- Store details about each game
- Monitor trends and changes to the store and its games over time
'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import uuid
from datetime import datetime
import requests
import json
from pathlib import Path
from bs4 import BeautifulSoup
import urllib.request
from selenium.webdriver.common.by import By

class Scraper:
    '''
    This is the Scraper function. It is used to scrape urls from the
    site's homepage and then information about each individual game
    Attribute:
        options(Options): A variable that only serves the purpose of allowing
        Selenium to run headless
        webpage(string): The url of the page you want to scrape
        driver(WebDriver): Used to specify the browser for selenium to use
        links(List): A list of urls pertaining to the webpage for each game
    '''

    def __init__(self, webpage) -> None:
        '''
        See help(Scraper) for accurate signature
        '''
        options = Options()
        options.headless = True
        self.webpage = webpage
        self.driver = webdriver.Chrome(options=options)
        self.links = []

    @staticmethod
    def accept_cookies(driver) -> None:
        '''
        This function is used to allow Selenium to click the
        'Accept Cookies' button on the site's mainpage

        Args:
            driver(WebDriver): The webdriver that selenium will be using
            to read the webpage

        Returns:
            None
        '''
        accept_cookies_button = driver.find_element(By.XPATH,
            '//*[@id="onetrust-accept-btn-handler"]')
        accept_cookies_button.click()

    def get_links(self):
        '''
        This function is used to return a list of the urls of
        games in the Epic Games Store

        Returns:
            self.links: A list of urls (str) pertaining to each individual game
        '''

        webpages = [self.webpage + '&count=100&start=' + str(i*100) for i in range(0,11)]

        for webpage in range(len(webpages)):
            self.driver.get(webpages[webpage])         
            time.sleep(10)

            if webpage == 0:
                Scraper.accept_cookies(self.driver)
                time.sleep(10)

            game_list = self.driver.find_elements(By.XPATH,
                '//*[@class="css-1jx3eyg"]')

            for game in game_list:
                link = game.get_attribute('href')
                self.links.append(link)

        return self.links

    @staticmethod
    def scrape_page_info(url):
        '''
        This is a static method that scrapes the useful information 
        of an epicgames.com game's url

        Args: url(string) the url that the user wishes to scrape.
        Though this is passed in via the method in main.

        Returns: game_dict(dictionary) A dictionary of useful attributes.
        Namely the title; the current and previous
        prices with the discount, if applicable;
        critics review scores; the name of the developer;
        the name of the publisher; the game's release date; and a list of photo urls
        '''
        html = requests.get(url).text
        page = BeautifulSoup(html, 'html.parser')

        # %%
        uuid = next(item for item in id_links if item["url"] == url)['id']

        # Scrape the title and the price changes individually
        title = page.find(attrs={'data-component': "PDPTitleHeader"}).text
        try:
            price_layout = page.find(
            attrs={'data-component': "PriceLayout"}).text.split('£')
        
        except Exception:
            price_layout = [None, None, None]

        if price_layout[0] == 'Free':
            discount, reduced_from_price, price = None, None, 0
        elif len(price_layout) != 3:
            discount, reduced_from_price, price = None, None, price_layout[1]
        else:
            discount, reduced_from_price, price = price_layout

        # Scrape the developer, publisher, and release date from a
        # sidebar element

        try:
            dirty_sidebar = page.find(attrs={
                'data-component': "SidebarMetadataLayout"}
            ).find_all(attrs={'data-component': 'Text'})

            sidebar = [i.text for i in dirty_sidebar]
            developer = sidebar[sidebar.index('Developer') + 1]
            publisher = sidebar[sidebar.index('Publisher') + 1]
            release_date = sidebar[sidebar.index('Release Date') + 1]
            release_date_as_datetime = datetime.strptime(
                release_date, '%m/%d/%y')
        except Exception:
            developer = None
            publisher = None
            release_date = None
            release_date_as_datetime = None

        # Scrape genre
        try:
            dirty_genre_list = page.find(attrs={
                'data-component': "MetadataList"}
            ).find_all(attrs={'data-component': 'Message'})
            genre_list = [i.text for i in dirty_genre_list]
        except Exception:
            genre_list = []

        # Scrape reviews

        try:
            dirty_critic = page.find(attrs={
                'data-component': "PDPCriticReviewMetricsLayout"}
            ).find_all(attrs={'class': 'css-1q9chu'})

            critics = [i.text for i in dirty_critic]

            critic_recommend = parse_percentage(critics[0])
            critic_top_average = critics[1]
        except Exception:
            critic_recommend = None
            critic_top_average = None

        # Scrape pictures

        try:
            dirty_pictures = page.find(attrs={'data-component': 'PDPCarousel'}
                                       ).find_all(
                attrs={'data-component': "Picture"})
            pictures = [i.find('img').get('src') for i in dirty_pictures]
            pictures = [pic for pic in pictures if not pic.
            startswith('https://catalogadmin')]
            #solves issue with picture scraping
        except Exception:
            pictures = []

        # Return a dictionary of all useful page details
        game_dict = {'uuid': uuid,'title': title, 'discounted from price': reduced_from_price,
                'price': price, 'developer': developer, 'publisher': publisher,
                'genre': genre_list, 'release date': release_date_as_datetime,
                'critics recommend': critic_recommend,
                'critic top average': critic_top_average,
                'pictures': pictures}
        
        return game_dict
    
    @staticmethod
    def scrape_images(folder_name, pictures):
        '''
        This is a static method used to scrape images and store them
        in the same folder is their respective json files

        Args:
            folder_name(string) the name of the folder within ./raw_data
            that the images will be saved into
            pictures(list) a list of the urls corresponding to each image
        
        Returns:
            None
        '''
        for j in range(len(pictures)):
            filename = './raw_data/' + folder_name + '/images/{}.jpg'.format(str(j))
            urllib.request.urlretrieve(pictures[j], filename)


def parse_percentage(str):
    '''
    Removes the percentage sign from a string and converts it to an integer
    Used to parse critic reviews
    '''
    return int(str.strip('%'))


if __name__ == "__main__":
    epicgames = Scraper(
        'https://www.epicgames.com/store/en-US/'
        'browse?sortBy=releaseDate&sortDir=DESC')
    list_of_games = epicgames.get_links()
    print('Finished generating links')

    # remove bundles
    my_filter = filter(lambda i: i.startswith(
        'https://www.epicgames.com/store/en-US/p'), list_of_games)
    list_of_games = list(my_filter)

    id_links = []
    for i in range(len(list_of_games)):
        id_links.append({'url': list_of_games[i], 'id': str(uuid.uuid4())})

    #create a folder to store the data
    Path('./raw_data').mkdir(parents=True, exist_ok=True)

    for i in range(len(id_links)):
        url = id_links[i]['url']
        game_info = epicgames.scrape_page_info(
            url)
        id = str(id_links[i]['id'])
        Path('./raw_data/' + id
             ).mkdir(parents=True, exist_ok=True)
        Path('./raw_data/' + id + '/images'
             ).mkdir(parents=True, exist_ok=True)
        filename = './raw_data/' + \
            id + '/' + 'data.json'
        with open(filename, 'w') as f:
            json.dump(game_info, f, indent=4, default=str)
        epicgames.scrape_images(id, game_info['pictures'])
    
    print('Finished scraping pages')
