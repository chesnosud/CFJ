""" Створені під окремий сайт парсери.
Що треба отримати: усю таблицю з сайту + href лінки

Способи:
1. Поєднання requests та BeautifulSoup
2. Поєднання pandas та BeautifulSoup (read_html - зручно, коли не треба href)
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup

def requests_beautifulsoup():
    
    url = 'http://www.vru.gov.ua/act_list'
    response = requests.get()
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')

    records = []
    columns = []
    for tr in table.findAll("tr"):
        ths = tr.findAll("th")
        if ths != []:
            for each in ths:
                columns.append(each.text)
        else:
            trs = tr.findAll("td")
            record = []
            for each in trs:
                try:
                    link = each.find('a')['href']
                    text = each.text
                    record.append(link)
                    record.append(text)
                except:
                    text = each.text
                    record.append(text)
            records.append(record)

    columns.insert(1, 'Link')
    df = pd.DataFrame(data=records, columns = columns)
    return df

def pandas_beautifulsoup():

    url = 'http://www.vru.gov.ua/act_list'
    df = pd.read_html(url)[0]

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')

    links = []
    for tr in table.findAll("tr"):
        trs = tr.findAll("td")
        for each in trs:
            try:
                link = each.find('a')['href']
                links.append(link)
            except:
                pass

    df['Link'] = links
    return df 