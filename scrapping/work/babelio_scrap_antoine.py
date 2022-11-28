import os
import logging
import urllib

import scrapy
from scrapy.crawler import CrawlerProcess
from functools import reduce


class BabelioScrapSpider(scrapy.Spider):
    name = 'babelio_scrap'
    allowed_domains = ['www.babelio.com']
    start_urls = ['https://www.babelio.com/livres/Wolfe-Le-bucher-des-vanites/7522']

    def parse(self, response):

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
            

            yield {
                "nom_auteur" : name,
                "prenom_auteur":surname,
                "titre" : title,
                "note" : com.xpath('.//meta[@itemprop="ratingValue"]/@content').get(),
                "commentaire" : com.xpath('.//div/div/text()').getall()
                }

        try:
            next_page = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[14]/a[@class="fleche icon-next"]').attrib["href"]
        except KeyError:
            logging.info('No next page. Terminating crawling process.')
        else:
            yield response.follow(next_page, callback=self.parse_critiques,meta={"title":title,"name":name,"surname":surname})

filename = "essai24_bis.json"

process = CrawlerProcess(settings = {
    'USER_AGENT': 'Chrome/105.0',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        'resultats/' + filename: {"format": "jsonlines"},
    }
})

process.crawl(BabelioScrapSpider)
process.start()
