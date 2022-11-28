import logging
import re # regexp
import scrapy
from scrapy.crawler import CrawlerProcess

def scrapping_runner(output_file, log_level = logging.INFO):
  logging.info(f"SCRAPING BEGIN")

  process = CrawlerProcess({
      "FEEDS":{rf"{output_file}" : { "format" : "json", "overwrite" : True }},
      'USER_AGENT' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
      'ROBOTSTXT_OBEY' : False,
      'AUTOTHROTTLE_ENABLED' : True,
      'AUTOTHROTTLE_START_DELAY' : 2,
      'AUTOTHROTTLE_MAX_DELAY' : 5,
      'LOG_LEVEL': log_level,
      'LOG_FORMAT':'%(asctime)s %(levelname)s: %(message)s',
      'REQUEST_FINGERPRINTER_IMPLEMENTATION':'2.7'
  })

  process.crawl(BabelioSpider)
  process.start()

class BabelioSpider(scrapy.Spider):
    global max_scrap_cities
    global cities_list_file
    global limit

    name = 'babelio'
    urls = ['https://www.babelio.com/livres/Devers-Les-liens-artificiels/1427352']

    def start_requests(self):
      for index,url in enumerate(self.urls):
          #yield scrapy.Request(url=url, callback=self.parse, meta={'index_url': index})
          yield scrapy.Request(url=url+'/critiques', callback=self.parse_comm, meta={'index_url': index})

    def parse(self, response):
        index_url = response.meta.get('index_url')
        yield self.__parse_book(response)

    def parse_comm(self, response):

        title = response.xpath("//h1/a/text()").get(default='').strip()
        comms = response.xpath("//div[@class='post']")

        list_comm = []
        for comm in comms:
            dic_comm = {
                'name' : comm.xpath(".//span[@itemprop='author']/span[@itemprop='name']/text()").get(default='')
            }
            list_comm.append(dic_comm)

        yield { 
          "comments" : list_comm,
          }

    def __parse_book(self, response):

        title = response.xpath("//h1/a/text()").get(default='').strip()
        author = response.xpath("string(//a[@class='livre_auteurs']/span)").get().strip()
        image_url = response.xpath("//div[@class='livre_con']/div/img/@src").get(default='')
        description = response.xpath("//div[@class='livre_resume']/text()").get(default='').strip()
        rating = response.xpath("//div[@itemprop='ratingValue']/text()").get(default='').strip()

        results = {
          "title" : title,
          "author": author,
          'image_url': image_url,
          'description': description,
          'rating': rating
          }

        return results

if __name__ == "__main__":
    scrapping_runner('output/scraping-julien.json')
