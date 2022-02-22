from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

# from instaparser.spiders.instagram import InstagramSpider
from instaparser.spiders.instagram2 import Instagram2Spider
from instaparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(Instagram2Spider)
    # process.crawl(InstagramSpider)

    process.start()
