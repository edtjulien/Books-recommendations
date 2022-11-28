import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
import os
import logging
from scrapy.crawler import CrawlerProcess
import config

def scrapping_runner(output_file, log_level = logging.INFO):
  logging.info(f"SCRAPING BEGIN")

  process = CrawlerProcess({
      "FEEDS":{rf"{output_file}" : { "format" : "jsonlines", "overwrite" : True }},
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

  process.crawl(BabelioSpider)
  process.start()

class BabelioSpider(scrapy.Spider):
    name = 'babelio-list-books'
    url_theme_ = 'https://www.babelio.com/livres-'
    url_ = 'https://www.babelio.com'

    def start_requests(self):
        for theme_name,theme_id in config.THEMES.items():
            end_url = f'/{theme_name}/{theme_id}'
            new_url = self.url_theme_ + end_url
            yield scrapy.Request(new_url, callback=self.parse_list_books, meta={'data' : {'theme_id': theme_id, 'theme_name': theme_name}})

    def parse_list_books(self, response):
        data = response.request.meta["data"]

        livres = response.xpath('//div[contains(@class, " list_livre")]')

        for livre in livres:
            url = livre.xpath('./a[1]/@href').get(default='')
            try:
                nb_comm = int(livre.xpath('./h3//a[1]/strong/text()').get(default='').strip())
            except:
                nb_comm = 0
                
            if ('livres/' in url and nb_comm >= config.NB_COMM_MIN): 
                yield {
                    'book_id': url.split('/')[-1],
                    'book_url': self.url_ + url,
                    'book_nb_comm': nb_comm,
                    **data,
                }
        
        try:
            next_page = response.xpath('//div[@id="id_pagination"]//a[@class="fleche icon-next"]').attrib["href"]
        except KeyError:
            logging.info('No next page. Terminating crawling process.')
        else:
            yield response.follow(next_page, callback=self.parse_list_books,meta={"data" : {**data}})


if __name__ == "__main__":
    scrapping_runner(config.LIST_BOOKS_FILE)
