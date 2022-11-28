import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
import os
import logging
from scrapy.crawler import CrawlerProcess

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

def bricole_url(dict_):
    s = []
    for k,v in dict_.items():
        s.append(f'{k}/{v}')
    return s

s = bricole_url(dic)

class BabelioSpider(scrapy.Spider):
    name = 'XXXXXXXX'
    url_ = 'https://www.babelio.com/livres-/'
#    start_urls = ['https://www.babelio.com/livres-/']
    links = s
    

    def start_requests(self):
        for el in s:
            new_url = self.url_+ el
            print(new_url)
            yield scrapy.Request(new_url, callback=self.search)

    def get_title(self, text):
        return text.split('par')[0].strip()
                
    def search(self, response):
        urls = response.xpath('//*[@class="list_livre_con"]/div/a/@href').getall()
        new_urls = self.url_ + urls
        print(new_urls)
        for i, url in enumerate(new_urls):
             if ('livres/' in url) and (i<1): 
                yield response.follow(url, callback=self.search_books)


    def search_books(self, response):
        title  = self.get_title(response.xpath("//*[@class='livre_con']/div/img/@title").get(default=''))
        author = response.xpath("string(//a[@class='livre_auteurs']/span)").get().strip()
        image_url = response.xpath("//div[@class='livre_con']/div/img/@src").get(default='')
        description = response.xpath("//div[@class='livre_resume']/text()").get(default='').strip()
        rating = response.xpath("//div[@itemprop='ratingValue']/text()").get(default='').strip()
        name = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[1]/div[2]/span[1]/a/span/text()').get(default="")
        surname = response.xpath('//*[@id="page_corps"]/div/div[3]/div[2]/div[1]/div[2]/span[1]/a/span/b/text()').get(default="")
        tags = ",".join([t.strip() for t in response.xpath('//*[@id="page_corps"]//p[@class="tags"]/a/text()').getall()])

        link = response.xpath("//*[@class='livre_header_links menu_item_anim']/a[@href][2]/text()").get(default='')

        results = {
          "title" : title,
          "author": author,
          "image_url": image_url,
          "description": description,
          "rating": rating,
          "name" : name,
          "surname" : surname,
          "tags" : tags
          }

        yield response.follow(link, callback=self.parse_critiques, meta=results)