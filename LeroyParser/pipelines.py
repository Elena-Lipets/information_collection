# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from pymongo import errors

class LeroyparserPipeline:

    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongobase = client.LM_goods_22_02_19

    def process_item(self, item, spider):
        item['_id'] = ''
        for el in item['url']:
            if el.isdigit():
                item['_id'] += el

        collection = self.mongobase.collection
        try:
            collection.insert_one(item)
        except errors.DuplicateKeyError:
            print(f'Документ с id {item.get("_id")}, именем {item.get("name")} уже в базе.')
        return item

    def process_id(self, link, spider_name):
        id = spider_name
        for el in link:
            if el.isdigit():
                id = id + el
        return id

class LeroyImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                new_link ='https://res.cloudinary.com/lmru/image/upload/LMCode/' + img.split('/')[-1]
                try:
                    yield scrapy.Request(new_link)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item


