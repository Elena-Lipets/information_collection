# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo import errors


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongobase = client.vacancies_22_03_15

    def process_item(self, item, spider):
        item['min_salary'], item['max_salary'], item['currency'] = self.process_salary(item.get('salary'), spider.name)
        item['_id'] = self.process_id(item.get('url'), spider.name)
        collection = self.mongobase[spider.name]
        try:
            collection.insert_one(item)
        except errors.DuplicateKeyError:
            print(f'Документ с id {item.get("_id")}, именем {item.get("name")} уже в базе.')
        print()
        return item

    def process_id(self, link, spider_name):
        id = spider_name
        for el in link:
            if el.isdigit():
                id = id + el
        return id


    def process_salary(self, initial_salary, spider_name):
        if spider_name == 'hhru':
            if initial_salary is None or len(initial_salary) == 1:
                # len(initial_salary) == 1 соответствует подписи "По договоренности" или "з/п не указана" в графе зарплата
                min_salary = None
                max_salary = None
                currency = None
            else:
                if initial_salary[0] == 'от ':
                    min_salary = int(initial_salary[1].replace('\xa0', ''))
                    if initial_salary[2] == ' до ':
                        max_salary = int(initial_salary[3].replace('\xa0', ''))
                        currency = initial_salary[5]
                    else:
                        max_salary = None
                        currency = initial_salary[3]

                elif initial_salary[0] == 'до ':
                    min_salary = None
                    max_salary = int(initial_salary[1].replace('\xa0', ''))
                    currency = initial_salary[3]

        elif spider_name == 'SJ':
            if initial_salary is None or len(initial_salary) == 1:
                # len(initial_salary) == 1 соответствует подписи "По договоренности" в графе зарплата
                min_salary = None
                max_salary = None
                currency = None
            else:
                if initial_salary[0] == 'от':
                    num = initial_salary[2].split('\xa0')
                    min_salary = int(''.join(num[0:2]))
                    max_salary = None
                    currency = num[2]
                elif initial_salary[0] == 'до':
                    num = initial_salary[2].split('\xa0')
                    min_salary = None
                    max_salary = int(''.join(num[0:2]))
                    currency = num[2]
                else:
                    min_salary = int(initial_salary[0].replace('\xa0', ''))
                    max_salary = int(initial_salary[4].replace('\xa0', ''))
                    currency = initial_salary[-3]

        return min_salary, max_salary, currency
