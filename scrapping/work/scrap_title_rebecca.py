import scrapy 
from scrapy.crawler import CrawlerProcess

class Projet_book_resume(scrapy.Spider):
    name = "projet_livre"
    
    start_urls = [
        'https://www.babelio.com/livres/Horvilleur-Il-ny-a-pas-de-Ajar/1428155'
    ]
    def parse(self, response):
        resume = response.xpath('//div[@class="livre_con"]')
        for i in resume:
            titre = i.xpath('.//div[@class="col col-4"]/img/@title').get()
            print(titre)
            
process = CrawlerProcess(settings = {
    'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
})#pareil mon user agent par rapport à mon ordi donc à modifier
process.crawl(Projet_book_resume) #j'ai pris un nom différent que celui des commentaires 
process.start()

#ici j'ai mi un print(car il y a que un titre par livre) mais on peut faire autrement pour récupérer l'info
