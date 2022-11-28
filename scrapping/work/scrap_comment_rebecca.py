import scrapy 
from scrapy.crawler import CrawlerProcess


class Projet_book(scrapy.Spider):
    name = "projet_books"
    
    start_urls = [
        'https://www.babelio.com/livres/Horvilleur-Il-ny-a-pas-de-Ajar/1428155/critiques'
    ]
    def parse(self, response):
        commentaires = response.xpath('//div[@class="post_con"]')
        for i in commentaires:
            pseudo = i.xpath('.//span[@itemprop="name"]/text()').get()
            text = i.xpath('.//div[@class= "text row"]/div/text()').getall()
            score = i.xpath('.//td[@style="text-align:right;"]/span/meta[2]/@content').get()
            like = i.xpath('.//div[@class="interaction post_items row"]/span/span[3]/span[2]/text()').get()
            date = i.xpath('.//td[@class="no_img"]/span/text()').get()
            yield {
                "pseudo": pseudo,
                "score":score,
                "like":like,
                "date":date,
                "text": text
            }

process = CrawlerProcess(settings = {
    'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'FEEDS': {
    "projet_book_essai" : {"format": "json"},#ou autre
    }

    
})

#alors j ai de base travailler sur un notebook pas script.. là j'ai pas esayer en script car je m'y connais,
#pas bien.. donc à vérifier si ça marche en script
#ici j'ai mon user agent par rapport à mon ordi donc à changer
#j ai fait pour un format json mais à bien être placer avant de l'enregistrer 
# ou à modifier la source d'enregistrement (vu que là j'étais sur julie j'ai fait ça comme ca )

process.crawl(Projet_book)
process.start()