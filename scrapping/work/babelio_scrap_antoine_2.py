import os
import logging
import urllib

import scrapy
from scrapy.crawler import CrawlerProcess
from functools import reduce
#import pandas as pd
#books=pd.read_csv("books.csv")



class BabelioScrapSpider(scrapy.Spider):

    name = 'babelio_scrap'
    allowed_domains = ['www.babelio.com']
    lien=input("lien")
    start_urls = [lien]

    def parse(self, response):

        name = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[1]/div[2]/span[1]/a/span/text()').get(default="")

        surname = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[1]/div[2]/span[1]/a/span/b/text()').get(default="")

        title = response.xpath('//*[@class="livre_header_con"]/h1/a/text()').get(default="")

        tags = ",".join([t.strip() for t in response.xpath('//*[@id="page_corps"]//p[@class="tags"]/a/text()').getall()])

        url=response.url+"/critiques"
        
        yield response.follow(url=url,callback=self.parse_critiques,meta={"title":title,"name":name,"surname":surname,"tags":tags})

    def parse_critiques(self,response):

        comments = response.xpath('//*[@class="post_con"]')

        name = response.request.meta["name"]

        surname = response.request.meta["surname"]

        title = response.request.meta["title"]

        tags = response.request.meta["tags"]

        for com in comments:
            
            url_profile = "https://www.babelio.com"+com.xpath('.//a[@class="author"]').attrib["href"]
            

            yield scrapy.Request(url=url_profile,callback=self.parse_profile,meta={
                                                                                    "name" : name,
                                                                                    "surname":surname,
                                                                                    "title" : title,
                                                                                    "tags" : tags,
                                                                                    "note" : com.xpath('.//meta[@itemprop="ratingValue"]/@content').get(default=""),
                                                                                    "date" : com.xpath('.//span[@class="gris"]/text()').get(default=""),
                                                                                    "appreciations" : com.xpath('.//span[@class="post_items_like "]/span[2]/text()').get(default=""),
                                                                                    "commentaire" : com.xpath("string(.//div[@class='text row']/div)").get(default="").strip() #[c.strip() for c in com.xpath('.//div/div/text()').getall()]
                                                                                    })

        try:
            next_page = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[14]/a[@class="fleche icon-next"]').attrib["href"]
        except KeyError:
            logging.info('No next page. Terminating crawling process.')
        else:
            yield response.follow(next_page, callback=self.parse_critiques,meta={"title":title,"name":name,"surname":surname,"tags":tags})

    def parse_profile(self,response):

        name=response.request.meta["name"]

        surname=response.request.meta["surname"]

        title=response.request.meta["title"]

        tags=response.request.meta["tags"]

        note=response.request.meta["note"]

        date = response.request.meta["date"]

        appreciations = response.request.meta["appreciations"]

        commentaire=response.request.meta["commentaire"]

        sex = response.xpath('//*[@id="page_corps"]/div/div[4]/div[1]/div[2]/div[2]/text()').get(default="")

        if sex.split(",")[0].strip()=="Femme" or sex.split(",")[0].strip()=="Homme":
            sexe = sex.split(",")[0].strip()
        else:
            sexe = "Inconnu"

        yield {
                "nom_auteur":name.strip(),
                "prenom_auteur":surname.strip(),
                "titre":title.strip(),
                "tags":tags,
                "note":note,
                "date":date,
                "appreciations":appreciations,
                "sexe_redacteur":sexe,
                "commentaire":commentaire.strip()
                }


filename = "essai1249.json"

process = CrawlerProcess(settings = {
    'AUTOTHROTTLE_ENABLED': True,
    'ROBOTSTXT_OBEY' : False,
    'DOWNLOAD_DELAY':2,
    'AUTOTHROTTLE_START_DELAY' : 2,
    'AUTOTHROTTLE_MAX_DELAY' : 10,
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        'resultats/' + filename: {"format": "jsonlines"},
    },
    "DOWNLOADER_MIDDLEWARES" : {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
#    'babelio.middlewares.BabelioDownloaderMiddleware': 543,
    }
})

process.crawl(BabelioScrapSpider)
process.start()
