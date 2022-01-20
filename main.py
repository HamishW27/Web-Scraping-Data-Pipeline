from inspect import isdatadescriptor
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

if __name__ == "__main__":
    page = requests.get(
        'https://www.epicgames.com/store/en-US/browse?sortBy=releaseDate&sortDir=DESC&count=40')
    html = page.text
    soup = BeautifulSoup(html, 'html.parser')
    # print(soup.prettify())

    driver = webdriver.Chrome()
    url = 'https://www.epicgames.com/store/en-US/browse?sortBy=releaseDate&sortDir=DESC&count=40'
    driver.get(url)
    time.sleep(5)

    accept_cookies_button = driver.find_element_by_xpath(
        '//*[@id="onetrust-accept-btn-handler"]')
    accept_cookies_button.click()

    game_list = driver.find_elements_by_xpath('//*[@class="css-1jx3eyg"]')

    for game in game_list:
        link = game.get_attribute('href')
        print(link)
