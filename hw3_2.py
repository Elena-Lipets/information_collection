from pymongo import MongoClient
from pprint import pprint


def vacancy_election(cutoff):
    client = MongoClient('127.0.0.1', 27017)
    db = client['vacancy_list_data']
    vacancy_collection = db.vacancy_collection
    for res in vacancy_collection.find({'currency': 'руб.', '$or': [{'min_salary': {'$gt': cutoff}},
                                                                   {'max_salary': {'$gt': cutoff}}]}):
        pprint(res)


vacancy_election(100000)
