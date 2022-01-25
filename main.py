import requests
from selenium import webdriver
import time

if __name__ == "__main__":
    driver = webdriver.Chrome()
    url = 'https://www.epicgames.com/store/en-US/browse?sortBy=releaseDate&sortDir=DESC&count=1000'
    driver.get(url)

    time.sleep(5)

    accept_cookies_button = driver.find_element_by_xpath(
        '//*[@id="onetrust-accept-btn-handler"]')
    accept_cookies_button.click()

    time.sleep(15)

    game_list = driver.find_elements_by_xpath('//*[@class="css-1jx3eyg"]')

    for game in game_list:
        link = game.get_attribute('href')
        print(link)
