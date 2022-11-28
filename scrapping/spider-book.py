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
    name = 'babelio-book'
    df_list_books = None
    
    def load_list_books(self, input_file):
        return pd.read_json(input_file, lines=True)

    def update_status_file(self, book_id):
        with open(config.STATUS_FILE.format(config.NAME_USER), "a+") as f:
            f.write(f"{book_id}\n")

    def load_list_status(self):
        try:
            with open(config.STATUS_FILE.format(config.NAME_USER), "r") as file:
                lines = [line.rstrip() for line in file]
                return lines
        except:
            return []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BabelioBookSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.engine_stopped, signal=signals.engine_stopped)
        signals.engine_stopped
        return spider

    # is execute in the end of all crawling
    def engine_stopped(self): # just get some stats to know the % of the total books to scrap
        if self.df_list_books is not None:
            total_books = self.df_list_books.shape[0]
            list_status = self.load_list_status()
            current_books_parsed = len(list_status)
            print('')
            print(f"##### {current_books_parsed} livres parsés sur {total_books} #####")
            print(f"##### {round((current_books_parsed / total_books)*100, 2)}% d'avancement #####")
            print('')
            if current_books_parsed < total_books:
                print(f'Courage {config.NAME_USER} !')
            else: print(f'Bravo {config.NAME_USER} !!! C\'est fini !')
            print('')

    def start_requests(self):
        self.df_list_books = self.load_list_books(config.LIST_BOOKS_FILE)
        list_status = self.load_list_status()

        i = 0
        for _, book in self.df_list_books.iterrows():
            if str(book['book_id']) in list_status: # pour reprendre où le scrapper s'était arrêté
                continue
            if i < config.BOOKS_BY_PARSING:
                i += 1
                yield scrapy.Request(book['book_url'], callback=self.parse, meta={'data' : {'book_id': book['book_id'], 'book_nb_comm':book['book_nb_comm']}})


    def parse(self, response):
        data = response.request.meta["data"]

        self.update_status_file(str(data['book_id']))

        name = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[1]/div[2]/span[1]/a/span/text()').get(default="").strip()
        surname = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[1]/div[2]/span[1]/a/span/b/text()').get(default="").strip()
        title = response.xpath('//*[@class="livre_header_con"]/h1/a/text()').get(default="").strip()
        img_url = response.xpath('//div[@class="livre_con"]/div/img/@src').get(default="").strip()
        tags = ",".join([t.strip() for t in response.xpath('//*[@id="page_corps"]//p[@class="tags"]/a/text()').getall()])

        url = response.url + "/critiques"
        
        yield response.follow(url=url,callback=self.parse_critiques,meta={"data" : {**data, "title":title,"name":name,"surname":surname,"tags":tags,"img_url":img_url}, "nb_comm_fornow":0})

    def parse_critiques(self,response):
        data = response.request.meta["data"]
        nb_comm_fornow = response.request.meta["nb_comm_fornow"]

        comments = response.xpath('//span[@itemprop="itemReviewed"]')

        for com in comments:       
            url_profile = "https://www.babelio.com"+com.xpath('.//a[@class="author"]').attrib["href"]
            try:
                user_id = url_profile.split('=')[1].strip()
            except:
                user_id = 0

            if nb_comm_fornow >= config.NB_COMM_MAX: #nb max de comm à parser atteint, on arrête
                break

            nb_comm_fornow += 1

            yield {
                **data,
                "comm_id" : com.xpath('.//div[@class="post_con"]/@id').get(default="").replace("B_CRI",""),
                "user_id" : user_id,
                "note" : com.xpath('.//meta[@itemprop="ratingValue"]/@content').get(default=""),
                "date" : com.xpath('.//span[@class="gris"]/text()').get(default=""),
                "appreciations" : com.xpath('.//span[@class="post_items_like "]/span[2]/text()').get(default="").strip(),
                "commentaire" : com.xpath("string(.//div[@class='text row']/div)").get(default="").strip()
                }
            
            # yield scrapy.Request(url=url_profile,callback=self.parse_profile,meta={"data" : {
            #                                                                         **data,
            #                                                                         "comm_id" : com.xpath('.//div[@class="post_con"]/@id').get(default="").replace("B_CRI",""),
            #                                                                         "note" : com.xpath('.//meta[@itemprop="ratingValue"]/@content').get(default=""),
            #                                                                         "date" : com.xpath('.//span[@class="gris"]/text()').get(default=""),
            #                                                                         "appreciations" : com.xpath('.//span[@class="post_items_like "]/span[2]/text()').get(default="").strip(),
            #                                                                         "commentaire" : com.xpath("string(.//div[@class='text row']/div)").get(default="").strip() #[c.strip() for c in com.xpath('.//div/div/text()').getall()]
            #                                                                         }})

        if nb_comm_fornow < config.NB_COMM_MAX: # on ne continue pas si on a assez de commentaires
            try:
                next_page = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[14]/a[@class="fleche icon-next"]').attrib["href"]
            except KeyError:
                logging.info('No next page. Terminating crawling process.')
            else:
                yield response.follow(next_page, callback=self.parse_critiques,meta={"data" : {**data}, "nb_comm_fornow":nb_comm_fornow})

    def parse_profile(self,response):
        data = response.request.meta["data"]

        sex = response.xpath('//*[@id="page_corps"]/div/div[4]/div[1]/div[2]/div[2]/text()').get(default="")
        if sex.split(",")[0].strip()=="Femme" or sex.split(",")[0].strip()=="Homme":
            sexe = sex.split(",")[0].strip()
        else:
            sexe = "Inconnu"

        yield {
                **data,
                "sexe_redacteur":sexe
                }


if __name__ == "__main__":
    scrapping_book_runner(config.FINAL_FILE.format(config.NAME_USER))
