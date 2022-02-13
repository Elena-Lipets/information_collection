from sys import argv
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from pymongo import MongoClient
from pymongo import errors

vacancy_type = argv
header = {'ACCEPT': 'application/vnd.github.v3+json',
          'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
url = 'https://hh.ru'
#params = {'text': vacancy_type[1]}
params = {'text': 'data '+'scientist'}
# params = {'text': 'data '+'scientist', 'page': 14}
response = requests.get(url=url+'/search/vacancy', params=params, headers=header)
client = MongoClient('127.0.0.1', 27017)
db = client['vacancy_list_data']
vacancy_collection = db.vacancy_collection
# vacancy_collection.delete_many({})
# vacancy_collection.create_index([('link', pymongo.TEXT)], name='link_index', unique=True)
# id = 0

while True:
    dom = BeautifulSoup(response.text, 'html.parser')
    vacancy_list = dom.select('div.vacancy-serp-item')
    for vacancy in vacancy_list:
        vacancy_info = {}
        # id += 1
        header_section = vacancy.find('a', {'class': 'bloko-link'})
        vacancy_info['name'] = header_section.getText()
        vacancy_info['link'] = header_section.get('href')
        vacancy_info['_id'] = hash(vacancy_info['link'])
        # vacancy_info['_id'] = id
        salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation',
                                       'class': ['bloko-header-section-3', 'bloko-header-section-3_lite']})
        if salary is None:
            vacancy_info['min_salary'] = None
            vacancy_info['max_salary'] = None
            vacancy_info['currency'] = None
        else:
            salary = salary.getText().split(' ')
            if salary[0] == 'от':
                vacancy_info['min_salary'] = int(''.join(salary[1].split('\u202f')))
                vacancy_info['max_salary'] = None
            elif salary[0] == 'до':
                vacancy_info['min_salary'] = None
                vacancy_info['max_salary'] = int(''.join(salary[1].split('\u202f')))
            else:
                vacancy_info['min_salary'] = int(''.join(salary[0].split('\u202f')))
                vacancy_info['max_salary'] = int(''.join(salary[2].split('\u202f')))
            vacancy_info['currency'] = salary[-1]
        vacancy_info['source_site'] = url

        if not vacancy_collection.find_one({'link': vacancy_info['link']}):
            try:
                vacancy_collection.insert_one(vacancy_info)
            except errors.DuplicateKeyError:
                print(f'Документ с id {vacancy_info["_id"]} уже существует')

    next_page = dom.find('a', {'data-qa': 'pager-next', 'class': 'bloko-button'})
    if next_page is None:
        break

    response = requests.get(url=url + next_page.get('href'), headers=header)

i = 0
for v in vacancy_collection.find({}):
    pprint(v)
    i += 1

print(i)


