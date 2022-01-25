import requests
from selenium import webdriver
import time


class Scraper:
    def __init__(self, webpage) -> None:
        self.webpage = webpage
        self.driver = webdriver.Chrome()

    def get_links(self):
        self.driver.get(self.webpage)

        time.sleep(5)
        accept_cookies_button = self.driver.find_element_by_xpath(
            '//*[@id="onetrust-accept-btn-handler"]')
        accept_cookies_button.click()

        time.sleep(15)

        game_list = self.driver.find_elements_by_xpath(
            '//*[@class="css-1jx3eyg"]')

        game_links = []

        for game in game_list:
            link = game.get_attribute('href')
            game_links.append(link)

        return game_links


if __name__ == "__main__":
    epicgames = Scraper(
        'https://www.epicgames.com/store/en-US/browse?sortBy=releaseDate&sortDir=DESC&count=1000')
    list_of_games = epicgames.get_links()

    print(list_of_games)
