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
    df_list_books = None
    
    def load_list_books(self, input_file):
        return pd.read_json(input_file, lines=True)

    def start_requests(self):
        self.df_list_books = self.load_list_books('output/list-books-noduplicate.json')

        for index, book in self.df_list_books.iterrows():
            if index <= 10900:
                 continue
            if index > 12000:
                break
            yield scrapy.Request(book['book_url'], callback=self.parse, meta={'data' : {'book_id': book['book_id'], 'book_url': book['book_url'], 'book_nb_comm':book['book_nb_comm']}})


    def parse(self, response):
        data = response.request.meta["data"]

        name = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[1]/div[2]/span[1]/a/span/text()').get(default="").strip()
        surname = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[1]/div[2]/span[1]/a/span/b/text()').get(default="").strip()
        title = response.xpath('//*[@class="livre_header_con"]/h1/a/text()').get(default="").strip()
        img_url = response.xpath('//div[@class="livre_con"]/div/img/@src').get(default="").strip()
        book_rating_count = response.xpath('//span[@itemprop="ratingCount"]/text()').get(default="").strip()
        book_rating_value = response.xpath('//span[@itemprop="ratingValue"]/text()').get(default="").strip()
        book_author_url = response.xpath('//span[@itemprop="author"]/a[@class="livre_auteurs"]/@href').get(default="").strip()
        book_editor = response.xpath('//div[contains(@class,"livre_refs")]/a/text()').get(default="").strip()

        try:
            refs = response.xpath('//div[contains(@class,"livre_refs")]').get(default="").strip()
            book_pages = int(refs.split('<br>')[1].replace('pages','').strip())
            book_date = refs.split('</a>')[1].replace('(','').replace(')','').replace('</div>','').strip()
        except:
            book_pages = 0
            book_date = ""
            

        tags = response.xpath('//*[@id="page_corps"]//p[@class="tags"]/a')
        tags_list = []
        for tag in tags:       
            try:
                name = tag.xpath('./text()').get(default="").strip()
                size = int(tag.xpath('./@class').get(default="").split(' ')[0].replace('tag_t',''))
                tags_list.append([name,size])
            except:
                continue

        tags_string = str(tags_list)

        yield {**data, "title":title,"name":name,"surname":surname,"tags":tags_string,
        "img_url":img_url,'book_rating_count':book_rating_count,'book_rating_value':book_rating_value,
        'book_author_url':book_author_url,'book_editor':book_editor,'book_pages':book_pages,'book_date':book_date}
        
if __name__ == "__main__":
    scrapping_book_runner(config.META_DATA_FILE)
