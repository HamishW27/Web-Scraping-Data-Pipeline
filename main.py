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
import json
from pathlib import Path


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
        self.driver = webdriver.Chrome()
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
        accept_cookies_button = driver.find_element_by_xpath(
            '//*[@id="onetrust-accept-btn-handler"]')
        accept_cookies_button.click()

    def get_links(self):
        '''
        This function is used to return a list of the urls of
        games in the Epic Games Store

        Returns:
            self.links: A list of urls (str) pertaining to each individual game
        '''
        self.driver.get(self.webpage)

        time.sleep(5)
        Scraper.accept_cookies(self.driver)
        time.sleep(20)

        game_list = self.driver.find_elements_by_xpath(
            '//*[@class="css-1jx3eyg"]')

        for game in game_list:
            link = game.get_attribute('href')
            self.links.append(link)

        return self.links

    @staticmethod
    def scrape_page_info(url, driver):
        driver.get(url)
        try:
            age_limit_button = driver.find_element_by_xpath(
                '//*[@data-component="BaseButton"]')
            age_limit_button.click()
            time.sleep(10)
        except Exception:
            pass
        title = driver.find_element_by_xpath('//h1').text
        price_layout = driver.find_element_by_xpath(
            '//*[@data-component="PriceLayout"]').text.split('\n')
        if len(price_layout) == 1:
            discount, reduced_from_price, price = None, None, price_layout[0]
        else:
            discount, reduced_from_price, price = price_layout
        try:
            sidebar = driver.find_element_by_xpath(
                '//*[@data-component="SidebarMetadataLayout"]'
            ).text.split('\n')
            developer = sidebar[sidebar.index('Developer') + 1]
            genre = driver.find_element_by_xpath(
                '//*[@data-component="Metadata"]').text.split('\n')[1:]
            release_date = sidebar[sidebar.index('Release Date') + 1]
            release_date_as_datetime = datetime.strptime(
                release_date, '%m/%d/%y')
        except Exception:
            developer, genre, release_date = None, None, None

        try:
            critic_bar = driver.find_element_by_xpath(
                '//*[@data-component="PDPCriticReviewMetricsLayout"]'
            ).text.split('\n')
            critic_recommend = parse_percentage(
                critic_bar[critic_bar.index('Critics Recommend') - 1])
            critic_top_average = critic_bar[critic_bar.index(
                'Top Critic Average') - 1]
        except Exception:
            critic_recommend = None
            critic_top_average = None

        return {'title': title, 'discounted from price': reduced_from_price,
                'price': price, 'developer': developer, 'genre': genre,
                'release date': release_date_as_datetime,
                'critics recommend': critic_recommend,
                'critic top average': critic_top_average}


def parse_percentage(str):
    return int(str.strip('%'))


if __name__ == "__main__":
    eg_url = 'https://www.epicgames.com/store/en-US/browse?sortBy=releaseDate&sortDir=DESC&count=1000'
    epicgames = Scraper(eg_url)
    list_of_games = epicgames.get_links()
    print('Finished generating links')

    url_data = []
    for i in range(len(list_of_games)):
        url_data.append({'url': list_of_games[i], 'id': str(uuid.uuid4())})

    Path('./raw_data').mkdir(parents=True, exist_ok=True)

    for i in range(len(url_data)):
        Path('./raw_data/' + str(url_data[i]['id'])
             ).mkdir(parents=True, exist_ok=True)
        game_info = epicgames.scrape_page_info(
            url_data[i]['url'], epicgames.driver)
        filename = './raw_data/' + \
            str(url_data[i]['id']) + '/' + str(url_data[i]['id']) + '.json'
        f = open(filename, 'x')
        with open(filename, 'w') as f:
            json.dump(game_info, f, indent=4, sort_keys=True, default=str)
