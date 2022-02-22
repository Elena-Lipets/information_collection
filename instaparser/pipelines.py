# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo import errors


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongobase = client.instagram

    def process_item(self, item, spider):
        collection = self.mongobase[item.get('target_username')]
        item['_id'] = item.get('user_id')
        try:
            collection.insert_one(item)
        except errors.DuplicateKeyError:
            print(f'Документ с id {item.get("_id")}, именем {item.get("username")} уже в базе.')
        return item
