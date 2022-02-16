import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjSpider(scrapy.Spider):
    name = 'SJ'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vakansii/uchitel-matematiki.html?geo%5Br%5D%5B0%5D=3']

    def parse(self, response: HtmlResponse):

        next_page = response.xpath("//span[contains(text(), 'Дальше')]/../../../@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//span[@class='_3a-0Y _3DjcL _3sM6i']//@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_pars)


    def vacancy_pars(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").get()
        salary = response.xpath("//span[@class='_1OuF_ ZON4b']//text()").getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)

