from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from pymongo import errors
import time

client = MongoClient('127.0.0.1', 27017)
db = client['e-mails']
mails = db.mails
mails.create_index('link', name='link_index', unique=True)

driver = webdriver.Chrome(executable_path='./chromedriver.exe')
driver.implicitly_wait(10)

driver.get('https://mail.ru/')
elem = driver.find_element(By.NAME, 'login')
elem.send_keys('study.ai_172')

elem = driver.find_element(By.XPATH, "//select[@name='domain']")
select = Select(elem)
select.select_by_value('@mail.ru')

elem = driver.find_element(By.XPATH, "//button[contains(text(), 'Ввести пароль')]")
elem.click()

# wait = WebDriverWait(driver, 10)
# elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']")))
elem = driver.find_element(By.XPATH, "//input[@name='password']")
elem.send_keys('NextPassword172#')
elem.send_keys(Keys.ENTER)

links_list = []
items = driver.find_elements(By.XPATH, "//a[contains(@class, 'llc_normal')]")
# items = driver.find_elements(By.XPATH, "//a[@data-draggable-id]")
# items = driver.find_elements(By.XPATH, "//a[contains(@class, 'llc')]")

for item in items:
    links_list.append(item.get_attribute('href'))
items[-1].send_keys(Keys.PAGE_DOWN)

while True:
    # wait = WebDriverWait(driver, 10)
    # items = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'llc_normal')]")))
    time.sleep(1)
    items = driver.find_elements(By.XPATH, "//a[contains(@class, 'llc_normal')]")
    if items[-1].get_attribute('href') == links_list[-1]:
        break
    # links_list = list(set(links_list))
    for item in items:
        links_list.append(item.get_attribute('href'))
    items[-1].send_keys(Keys.PAGE_DOWN)

# print(len(links_list))
links_list = list(set(links_list))
# print(len(links_list))

for link in links_list:
    mail = {}
    driver.get(link)
    mail['link'] = link
    # time.sleep(1)
    wait = WebDriverWait(driver, 15)
    mail['from'] = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='letter__author']//"
                                                 "span[contains(@class, 'letter-contact')]"))).text
    # mail['from'] = driver.find_element(By.XPATH, "//div[@class='letter__author']//"
    #                                              "span[contains(@class, 'letter-contact')]").text
    mail['send_at'] = driver.find_element(By.XPATH, "//div[@class='letter__date']").text
    mail['theme'] = driver.find_element(By.XPATH, "//h2[@class='thread-subject']").text
    mail['mail_text'] = driver.find_element(By.CLASS_NAME, 'letter-body__body-content').text
    # driver.back()
    try:
        mails.insert_one(mail)
    except errors.DuplicateKeyError:
        print(f'Письмо {mail["theme"]} уже в базе')
