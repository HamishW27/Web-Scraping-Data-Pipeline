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
from tqdm import tqdm
import glob
import os
import re
import pandas as pd
import json
import boto3
from sqlalchemy import create_engine
from certification import *

'''
For security, this program requires a file named certification.py 
formatted as follows in this same directory:

from sqlalchemy import create_engine
DATABASE_TYPE = 'postgresql'
DBAPI = 'psycopg2'
ENDPOINT = #Name of AWS Endpoint
USER = 'postgres'
PASSWORD = #RDS User Password
PORT = 5432
DATABASE = 'postgres'
engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
'''

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
            self.links(List): A list of urls (str) pertaining to each individual game
        '''

        webpages = [self.webpage + '&count=40&start=' + str(i*40) for i in range(0,28)]

        for webpage in tqdm(range(len(webpages)), desc='Getting page links'):
            self.driver.get(webpages[webpage])         
            time.sleep(5)

            if webpage == 0:
                Scraper.accept_cookies(self.driver)
                time.sleep(5)

            game_list = self.driver.find_elements(By.XPATH,
                '//*[@class="css-1jx3eyg"]')

            for game in game_list:
                link = game.get_attribute('href')
                self.links.append(link)

        return self.links

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
        html = requests.get(url).text
        page = BeautifulSoup(html, 'html.parser')

        uuid = next(item for item in url_and_ids if item["url"] == url
        )['id']

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
            discount = parse_percentage(discount)

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
        game_dict = {'uuid': uuid, 'url': url, 'title': title, 'discounted from price': reduced_from_price,
                'price': price, 'discount': discount, 'developer': developer, 'publisher': publisher,
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

    Args:
        str(string): A string pertaining to a review as a percent
        containing ampersand(s)
    
    Returns:
        int(str.strip('%'))(Integer): An integer equal to the 
        numerical representation of the percentage of str
    '''
    return int(str.strip('%'))

def create_folders(id):
    '''
    Function used to generate folders in the filesystem in which to
    store the images and json file of the scraped webpage

    Args:
        id(string): UUID4 as string
    
    Returns:
        None
    '''
    Path('./raw_data/' + id
             ).mkdir(parents=True, exist_ok=True)
    Path('./raw_data/' + id + '/images'
             ).mkdir(parents=True, exist_ok=True)

def flatten(t):
    '''
    Function to 'flatten' a list ie. to generate a single list of items 
    from a list of lists containing multiple items 

    Args:
        t(List): A list containing multiple lists
    
    Returns:
        Unnamed(List): A List of items within the
        lists inside of the list in the argument
    '''
    return [item for sublist in t for item in sublist]

def find_existing_table(table_name, column_name):
    '''
    Finds a column of ids in a database using the
    SQLAlchemy engine imported from certification.py

    Args:
        table_name (string): The name of the table in the
        database in which the column of ids is stored
        column_name (string): The name of the column within the database
        in which the ids are stored
    
    Returns:
        Unnamed(List): A list of the ids of games stored in the database
    '''
    try:
        ids = pd.read_sql_table(table_name, engine, columns=[column_name])
        return flatten(ids.values.tolist())
    except:
        return []

def read_into_table(json_location):
    '''
    Generates a database from locally stored files to ensure that 
    duplicate files are not scraped in the interest of reducing runtime

    Args:
        json_location(string): The location of the raw_data folder 
        in which json files and images are stored
    
    Returns:
        game_df(pandas.DataFrame): A Dataframe containing all the info
        scraped about every game whose files exist locally
    '''
    file_list = []

    os.listdir()
    for file in glob.glob(json_location):
        file_list.append(file)
    
    dfs = [] # an empty list to store the data frames
    
    for file in file_list:
        with open(file) as json_file:
            data = json.load(json_file)
            df = pd.json_normalize(data)
            dfs.append(df)

    game_df = pd.concat(dfs, ignore_index=True)
    return game_df

def upload_table(df_name, output_name):
    '''
    Uploads a dataframe to a database

    Args:
        df_name(pd.Dataframe): The name of the dataframe to be uploaded
        output_name(string): The name to give to the table being uploaded

    Returns:
        None 
    '''
    df_name.to_sql(output_name, engine, if_exists='append')

def read_photos_into_table(json_dataframe):
    '''
    Reads scraped local image data into a dataframe

    Args:
        json_dataframe(pd.Dataframe): The name of the 'games' table
        in the database containing local image data. 
        This is used to create a table of images
    
    Returns:
        picture_df(pd.Dataframe): A table of information about the images
        scraped containing ids, urls, image names, and the id of the 
        game they belong to
    '''
    dfs = []
    for index, row in json_dataframe.iterrows():
        id = row['uuid']
        pictures = row['pictures']
        filenames = sorted(glob.glob("raw_data/{}/images/*.jpg".format(id)))
        for num, picture in enumerate(pictures):
            game_uuid = re.sub('/images/.*\.jpg','',filenames[num])
            game_uuid = re.sub('raw_data/','', game_uuid)
            df_part = {'photo_uuid':uuid.uuid4(), 'url':picture, 'img_name':filenames[num], 'game_uuid':game_uuid}
            df_part = pd.DataFrame(df_part, index=[0])
            dfs.append(df_part)
        
    picture_df = pd.concat(dfs, ignore_index=True)

    return picture_df


def uploadDirectory(path,bucketname):
    s3_client = boto3.client('s3')
    s3 = boto3.resource('s3')
    for root,dirs,files in os.walk(path):
        for file in files:
            s3_client.upload_file(os.path.join(root,file),bucketname,file)

if __name__ == "__main__":
    existing_urls = find_existing_table('games', 'url')
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

    #scrape each page and download the information
    for i in tqdm(range(len(id_links)), desc='Scraping pages'):
        url = id_links[i]['url']
        if url in existing_urls:
            continue
        game_info = epicgames.scrape_page_info(
        url, id_links)
        id = str(id_links[i]['id'])
        create_folders(id)
        epicgames.scrape_images(id, game_info['pictures'])
        filename = './raw_data/' + \
            id + '/' + 'data.json'
        with open(filename, 'w') as f:
            json.dump(game_info, f, indent=4, default=str)
    
    print('Finished scraping pages')

    try:
        game_dataframe = read_into_table("./raw_data/*/*.json")
        upload_table(game_dataframe, 'games')
    except ValueError:
        print('No new games to add')
    
    try:
        photo_dataframe = read_photos_into_table(game_dataframe)
        upload_table(photo_dataframe, 'images')
    except NameError:
        print('No new images to add')
    
    try:
        uploadDirectory('./raw_data', 'aicorescraperhamishw')
        print('Uploaded data to bucket')
    except Exception:
        print('Nothing to upload')

    print('Tables uploaded')