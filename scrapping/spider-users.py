import scrapy
from scrapy import signals
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
import os
import logging
import pandas as pd
from scrapy.crawler import CrawlerProcess
import config

def scrapping_book_runner(output_file, log_level = logging.INFO):
  logging.info(f"SCRAPING BEGIN")

  process = CrawlerProcess({
      "FEEDS":{rf"{output_file}" : { "format" : "jsonlines", "overwrite" : False }},
      'USER_AGENT' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
      'ROBOTSTXT_OBEY' : False,
      'AUTOTHROTTLE_ENABLED' : True,
      'AUTOTHROTTLE_START_DELAY' : 5,
      'AUTOTHROTTLE_MAX_DELAY' : 10,
      'DOWNLOAD_DELAY' : config.DOWNLOAD_DELAY,
      'CONCURRENT_REQUESTS' : 1,
      'CONCURRENT_REQUESTS_PER_DOMAIN' : 1,
      'LOG_LEVEL': log_level,
      'LOG_FORMAT':'%(asctime)s %(levelname)s: %(message)s',
      'REQUEST_FINGERPRINTER_IMPLEMENTATION':'2.7'
  })

  process.crawl(BabelioBookSpider)
  process.start()

class BabelioBookSpider(scrapy.Spider):
    name = 'babelio-book-meta'
    root_url = 'https://www.babelio.com/monprofil.php?id_user={}'
    
    def load_list_users(self, input_file):
        return pd.read_csv(input_file)

    def start_requests(self):
        self.df_list_users = self.load_list_users('output/users.csv')

        for index, user_row in self.df_list_users.iterrows():
            if index <= 13500:
                 continue
            if index > 14000:
                break
            yield scrapy.Request(self.root_url.format(user_row['users']), callback=self.parse, meta={'user_id': user_row['users']})


    def parse(self, response):
        user_id = response.request.meta["user_id"]

        try:
            gender = response.xpath('//div[@class="livre_con"]//div[@class="livre_refs"][1]/text()').get(default="").split(',')[0].strip().lower()
            if gender == "femme":
                gender = "F"
            elif gender == "homme":
                gender = 'M'
            else: gender = ""
        except:
            gender = ""
        

        yield {"user_id":str(user_id), "gender":gender}
        
if __name__ == "__main__":
    scrapping_book_runner(config.USERS_FILE)
