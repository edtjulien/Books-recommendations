import logging
import re # regexp
import scrapy
from scrapy.crawler import CrawlerProcess

def bricole_url(dict_):
    s = []
    for k,v in dict_.items():
        s.append(f'{k}/{v}')
    return s

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
    name = 'babelio'
    start_url = 'https://www.babelio.com/livres-/'

    dic = {'aventure' : 33,
       'romans-policiers-et-polars' : 63883,
       'cinema' : 89,
       'roman' : 1,
       'biographie' : 31,
       'humour' : 15,
       'science-fiction' : 6,
       'thriller' : 11,
       'fantastique' : 7,
       'amour' : 77}

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.links = bricole_url(self.dic)

    def start_requests(self):
        url_test = "https://www.babelio.com/livres/Pasques-Fils-de-personne/1466172"

        yield scrapy.Request(url_test, callback=self.parse)
        # for el in self.links:
        #     new_url = self.start_url + el
        #     yield scrapy.Request(new_url, callback=self.parse)
     
    def parse(self, response):
        urls = response.xpath('//*[@class="list_livre_con"]/div/a/@href').getall()
        new_urls = self.start_urls + urls
        for url in new_urls:
            yield{
                'url': url
            }
            yield response.follow(url, callback=self.parse_book)
    
    def parse_book(self, response):
        name = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[1]/div[2]/span[1]/a/span/text()').get()
        surname = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[1]/div[2]/span[1]/a/span/b/text()').get()
        title = response.xpath('//*[@class="livre_header_con"]/h1/a/text()').get()
        url=response.url+"/critiques"

        yield response.follow(url=url,callback=self.parse_critiques,meta={"title":title,"name":name,"surname":surname})

    def parse_critiques(self,response):
        comments = response.xpath('//*[@class="post_con"]')
        name = response.request.meta["name"]
        surname = response.request.meta["surname"]
        title = response.request.meta["title"]

        for com in comments:
            url_profile = "https://www.babelio.com"+com.xpath('.//a[@class="author"]').attrib["href"]
            yield scrapy.Request(url=url_profile,callback=self.parse_profile,meta={
                                                                                    "name" : name,
                                                                                    "surname":surname,
                                                                                    "title" : title,
                                                                                    "note" : com.xpath('.//meta[@itemprop="ratingValue"]/@content').get(),
                                                                                    "commentaire" : com.xpath('.//div/div/text()').getall()
                                                                                    })

        try:
            next_page = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[14]/a[@class="fleche icon-next"]').attrib["href"]
        except KeyError:
            logging.info('No next page. Terminating crawling process.')
        else:
            yield response.follow(next_page, callback=self.parse_critiques,meta={"title":title,"name":name,"surname":surname})

    def parse_profile(self,response):
        name=response.request.meta["name"]
        surname=response.request.meta["surname"]
        title=response.request.meta["title"]
        note=response.request.meta["note"]
        commentaire=response.request.meta["commentaire"]
        sex = response.xpath('//div[@class="livre_con"]//div[@class="livre_refs"]/text()').get()

        sexe = sex.split(",")[0].strip()
        if sexe != "Femme" and sexe != "Homme":
            sexe = ""

        yield {
                "prenom_auteur":name,
                "nom_auteur":surname,
                "titre":title,
                "note":note,
                "sexe":sexe,
                "commentaire":commentaire
                }

if __name__ == "__main__":
    scrapping_runner('output/scraping.json', logging.DEBUG)
