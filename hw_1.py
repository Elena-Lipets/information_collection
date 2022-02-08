import requests
import json
#from pprint import pprint

header = {'ACCEPT': 'application/vnd.github.v3+json', 'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
user = 'Elena-Lipets'
response = requests.get(url=f"https://api.github.com/users/{user}/repos", headers=header)

EL_repos = response.json()
# pprint(EL_repos)
print(f"Список репозиториев пользователя {user}:")
for i in EL_repos:
    print(i.get('name'))
with open('EL_repos.json', 'w') as f:
    json.dump(response.json(), f)
