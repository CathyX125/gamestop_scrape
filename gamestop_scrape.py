import re
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import requests
from time import sleep
from collections import Counter
import pandas as pd
from datetime import datetime
from selenium import webdriver
import csv
import time

driver = webdriver.Firefox()

def get_list(page):
    url = f"https://www.gamespot.com/games/reviews/?page={page}"
    driver.get(url)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    section = soup.find('section', class_="editorial river")

    for div in section.find_all('div', class_="horizontal-card-item"):
        yield div.find('a', class_="horizontal-card-item__link").get("href")


def get_page(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.text
    except:
        pass

    try:
        driver.get(url)
        return driver.page_source
    except:
        pass

    return None


def get_game_detail(url):
    page = get_page(url)
    if page is None:
        return None, None, None, None, None, None, None, None

    try:
        soup = BeautifulSoup(page, 'lxml')
        score = soup.find('div', class_="review-ring-score__score").get_text(strip = True)
        try:
            platform = [ x.get_text(strip = True) for x in soup.find('ul', class_="system-list").find_all('li')]
        except:
            platform = None

        pod = soup.find('div', class_="game-module pod")
        name = pod.find('a').get_text(strip = True)
        release_date = pod.find('div', class_="game-module__release-date").span.get_text(strip = True)
        developer = [x.get_text(strip = True) for x in pod.find('div', class_="game-module__developers").find_all('li')]
        publisher = [x.get_text(strip = True) for x in pod.find('div', class_="game-module__publishers").find_all('li')]
        genres = [x.get_text(strip = True) for x in pod.find('div', class_="game-module__genres").find_all('li')]
        platform_all = [ x.get_text(strip = True) for x in set(pod.find('ul', class_="game-module__platform").find_all('li')) - set(pod.find_all('li', class_=lambda x: "unhide" in x))]
        if platform is None:
            platform = platform_all

        return(name, release_date, score, platform, platform_all, developer, publisher, genres)
    except:
        return None, None, None, None, None, None, None, None


if __name__ == "__main__":
    l = []
    index = 0
    for i in range(1, 701):
        for j in get_list(i):
            url = "https://www.gamespot.com"+j
            index+=1
            l.append((index, url))
            with open(r'url_list.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow((index, url))

    url = pd.read_csv('url_list.csv', header = None)
    exist_items = set(pd.read_csv('scraped_data.csv', header = None).T.values.tolist()[0])

    start_time = time.time()
    last_stop_at = 0
    for i in range(last_stop_at, 14701):
        index = i+1
        print(index)
        if index in exist_items:
            continue

        sleep(1)
        link = url.iloc[i][1]
        name, release_date, score, platform, pa, developer, publisher, genres = get_game_detail(link)
        if name is None:
            continue
        with open(r'scraped_data.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow((index, name, release_date, score, platform, pa, developer, publisher, genres))
        print(name, score)
        elapsed_time = time.time() - start_time
        print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

    driver.quit()

