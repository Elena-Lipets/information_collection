from sys import argv
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import pandas

vacancy_type = argv
header = {'ACCEPT': 'application/vnd.github.v3+json',
          'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
url = 'https://hh.ru'
params = {'text': vacancy_type[1]}
# params = {'text': 'data '+'scientist'}
# params = {'text': 'data '+'scientist', 'page': 14}
response = requests.get(url=url+'/search/vacancy', params=params, headers=header)
vacancy_list_data = []
while True:
    dom = BeautifulSoup(response.text, 'html.parser')
    vacancy_list = dom.select('div.vacancy-serp-item')
    for vacancy in vacancy_list:
        vacancy_info = {}
        header_section = vacancy.find('a', {'class': 'bloko-link'})
        vacancy_info['name'] = header_section.getText()
        vacancy_info['link'] = header_section.get('href')
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
        # wright_order = {'name': 1, 'link': 2, 'min_salary': 3, 'max_salary': 4, 'currency': 5, 'source_site': 6}
        # sorted(vacancy_info, key=lambda item: wright_order.get(item[0]))
        vacancy_list_data.append(vacancy_info)

    next_page = dom.find('a', {'data-qa': 'pager-next', 'class': 'bloko-button'})
    if next_page is None:
        break

    response = requests.get(url=url + next_page.get('href'), headers=header)

result = pandas.DataFrame(vacancy_list_data)
result.to_csv('result.csv')
pprint(vacancy_list_data)

