# Web-Scraping-Data-Pipeline

> This is a Web Scraper built with selenium and bs4. Its goal is to download information on the games in the Epic Games Store.  

## Milestone 1

- The Selenium webdriver is used to scrape the list of games that the Epic Games store provides. I wish to use this knowledge to find trends in genre over time as well as to track price changes. The scraper can be run inside of a docker container available at Docker Hub.

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

- Now that the list of games has been scraped, BeautifulSoup is used to constrict a dictionary of useful information about each game. This is preferable to using Selenium as the data is contained in the html file of each game's page and therefore establishing a connection to each webpage is redundant and costs time. 

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

## Milestone 3

- Used urllib and pandas to download images and json information and store them within the filesystem. Path was used to create appropriate directories.

```python
def create_folders(id):
    Path('./raw_data/' + id
             ).mkdir(parents=True, exist_ok=True)
    Path('./raw_data/' + id + '/images'
             ).mkdir(parents=True, exist_ok=True)
```

## Milestone 4

- Introduced a test.py file to run unit tests. These test that the functions return specific expected links or file types.

```python
def test_get_links(self):
        epicgames = Scraper(
        'https://www.epicgames.com/store/en-US/'
        'browse?sortBy=releaseDate&sortDir=DESC&count=1000')
        expected_item = 'https://www.epicgames.com/store/en-US/p/grand-theft-auto-v'
        actual_items = epicgames.get_links()
        self.assertIn(expected_item, actual_items)
```

## Milestone 5 

- Added methods to scalably store data using AWS. Files detailing information about images and games are uploaded to RDS and actual files are backed up to S3. Tables are constructed using SQLAlchemy and pandas dataframes. 

```python
def upload_table(df_name, output_name):
    df_name.to_sql(output_name, engine, if_exists='append')
```

## Milestone 6

- Updated the scraper to run inside of an AWS EC2 instance. This involved rewriting code to decrease memory usage so the program could run on the resources of a micro instance; changing seleniums settings to allow it to run in headless mode; building a docker container to run the python script. Games are compared with data inside of the tables before scraping to reduce runtime and ensure that pages are not scraped twice.

```docker
docker run -p 5900:5900 --user scraperuser --privileged --shm-size="2g" -w /home/scraperuser hamishw27/egwebscraper:v1
```

## Milestone 7

- Enabled Docker metrics and edited the AWS security group to access the data from a computer on a different network. Using prometheus and grafana, the instance and the container can be monitored for usage spikes and help the user to discover errors. This allows the scraper to run uninterrupted on an EC2 instance.

```yaml
- job_name: docker
  honor_timestamps: true
  scrape_interval: 15s
  scrape_timeout: 10s
  metrics_path: /metrics
  scheme: http
  follow_redirects: true
```

## Milestone 8

The final update to my project involved creating a CI/CD Pipeline to automate the docker build process through a custom GitHub action. After this the EC2 instance has been automated through the creation of cron jobs to pull the latest image and run the project daily. This means that all that needs to be done manually is to push any future changes to GitHub and this will in turn update the instance.

```yaml
name: Login to Docker Hub
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_ACCESS_TOKEN }}
```