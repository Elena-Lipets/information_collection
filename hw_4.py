import requests
from lxml import html
from pymongo import MongoClient
# from pymongo import errors
from pprint import pprint

url = 'https://yandex.ru/news'
header = {'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/97.0.4692.71 Safari/537.36'}
client = MongoClient('127.0.0.1', 27017)
db = client['yandex_news']
main_news = db.main_news
response = requests.get(url=url, headers=header)
dom = html.fromstring(response.text)

items = dom.xpath("//div[contains(@class, 'news-top-flexible-stories')]//div[contains(@class, 'mg-grid__col_xs_')]")
for item in items:
    a_piece_of_news = {}
    a_piece_of_news['_id'] = item.xpath(".//h2/a/@href")[0]
    a_piece_of_news['yandex_time'] = item.xpath(".//span[@class='mg-card-source__time']/text()")[0]
    a_piece_of_news['source'] = item.xpath(".//a[@class='mg-card__source-link']/text()")[0]
    url = a_piece_of_news.get('_id')
    response = requests.get(url=url, headers=header)
    dom = html.fromstring(response.text)
    a_piece_of_news['name'] = dom.xpath("//h1[@class='mg-story__title']/a/text()")[0].replace('\xa0', ' ')
    a_piece_of_news['link'] = dom.xpath("//h1[@class='mg-story__title']/a/@href")[0]
    url = a_piece_of_news.get('link')
    response = requests.get(url=url, headers=header)
    dom = html.fromstring(response.text)
    a_piece_of_news['date_time'] = dom.xpath("//time/text()")[0]
    pprint(a_piece_of_news)
    main_news.replace_one({'_id': a_piece_of_news.get('_id')}, a_piece_of_news, upsert=True)
