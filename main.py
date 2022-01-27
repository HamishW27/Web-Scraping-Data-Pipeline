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
    This is the initialistion function
    Attribute: 
        webpage(string): The url of the page you want to scrape
        driver(WebDriver): Used to specify the browser for selenium to use

    '''

    def __init__(self, webpage) -> None:
        self.webpage = webpage
        self.driver = webdriver.Chrome()
        self.links = []

    @staticmethod
    def accept_cookies(driver):
        accept_cookies_button = driver.find_element_by_xpath(
            '//*[@id="onetrust-accept-btn-handler"]')
        accept_cookies_button.click()

    def get_links(self):
        self.driver.get(self.webpage)

        time.sleep(5)
        Scraper.accept_cookies(self.driver)

        time.sleep(15)

        game_list = self.driver.find_elements_by_xpath(
            '//*[@class="css-1jx3eyg"]')

        for game in game_list:
            link = game.get_attribute('href')
            self.links.append(link)


if __name__ == "__main__":
    epicgames = Scraper(
        'https://www.epicgames.com/store/en-US/browse?sortBy=releaseDate&sortDir=DESC&count=1000')
    epicgames.get_links()

    print(epicgames.links)
