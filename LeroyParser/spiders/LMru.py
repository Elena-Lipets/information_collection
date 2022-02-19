import scrapy
from scrapy.http import HtmlResponse
from LeroyParser.items import LeroyparserItem
from scrapy.loader import ItemLoader


class LmruSpider(scrapy.Spider):
    name = 'LMru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search, **kwargs):
        super().__init__(search, **kwargs)
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}&fromRegion=34&eligibilityByStores=Зеленоград&page=17']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa-pagination-item='right']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@data-qa='product-name']")
        for link in links:
            yield response.follow(link, callback=self.pars_ads)



    def pars_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyparserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('photos', "//img[@slot='thumbs']/@src | //uc-variant-card//img/@src")
        loader.add_value('url', response.url)
        yield loader.load_item()

        # name = response.xpath('//h1/text()').get()
        # price = response.xpath("//span[@slot='price']/text()").get()
        # photos = response.xpath("//img[@slot='thumbs']/@src | //uc-variant-card//img/@src").getall()
        # url = response.url
        # yield LeroyparserItem(name=name, price=price, photos=photos, url=url)




