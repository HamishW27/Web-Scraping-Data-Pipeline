'''
This is a scraper module specifically for use with the website 
"https://www.epicgames.com/store/en-US/." 
it contains the Scraper class which allows you to:
- Scrape the homepage for links to games
- Scrape details about each game from their respective pages
- Store details about each game
- Monitor trends and changes to the store and its games over time
'''

import requests
from selenium import webdriver
import time


class Scraper:
    '''
    This is the Scraper function. It is used to scrape urls from the 
    site's homepage and then information about each individual game
    Attribute: 
        webpage(string): The url of the page you want to scrape
        driver(WebDriver): Used to specify the browser for selenium to use
        links(List): A list of urls pertaining to the webpage for each game
    '''

    def __init__(self, webpage) -> None:
        '''
        See help(Scraper) for accurate signature
        '''
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

        self.driver.close()

        return self.links


if __name__ == "__main__":
    epicgames = Scraper(
        'https://www.epicgames.com/store/en-US/browse?sortBy=releaseDate&sortDir=DESC&count=1000')
    list_of_games = epicgames.get_links()

    print(list_of_games)
