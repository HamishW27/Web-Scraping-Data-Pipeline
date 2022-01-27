import requests
from selenium import webdriver
import time


class Scraper:
    def __init__(self, webpage, bool_accept_cookies=False) -> None:
        self.webpage = webpage
        self.driver = webdriver.Chrome()
        self.bool_accept_cookies = bool_accept_cookies
        self.links = []

    @staticmethod
    def accept_cookies(driver):
        accept_cookies_button = driver.find_element_by_xpath(
            '//*[@id="onetrust-accept-btn-handler"]')
        accept_cookies_button.click()

    def get_links(self):
        self.driver.get(self.webpage)

        if self.bool_accept_cookies == True:
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
        'https://www.epicgames.com/store/en-US/browse?sortBy=releaseDate&sortDir=DESC&count=1000', bool_accept_cookies=True)
    epicgames.get_links()

    print(epicgames.links)
