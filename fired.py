"""
Виправити "Суд", зокрема щодо апеляційних/господарських
"""

import re, sys
import requests, datetime
import pandas as pd
from bs4 import BeautifulSoup

def parse_vrp(url):
    """Отримую дані з сторінки актів врп"""

    response = requests.get(url)
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
    return pd.DataFrame(data=records, columns = columns)

def filter_data(dataframe):
    """
    Відбираю з отриманих результатів ті, що стосуються звільнень; 
    отримую з тексту ім'я;
    в результаті додаю нові колонки.
    """

    df = dataframe.copy()
    df = df.loc[df['Назва документу'].str.contains('звільн', case=False)]
    df = df.loc[~df['Назва документу'].str.contains('залишення без розгляду', case=False)]
    df = df.loc[df['Назва документу'].str.contains('суду', case=False)]
    df['Піб'] = df['Назва документу'].str.extract(r'(\w+\s\w\.\w\.)')
    df['id'] = 'xxxxx'
    df['Суд'] = 'xxxxx'
    df = df[['id', 'Піб', 'Суд', 'Дата прийняття', 'Link', 'Назва документу']]
    return df[::-1]

def add_info(df):
    """З тексту отримую назву суду та підставу для звільнення."""

    container = []
    for i in df['Назва документу']:
        try:
            m = re.search(r'(\w+[^\s]\w+\s\w+\s\суду\s\w+\s\w+)', i).group(1)
        except:
            m = re.search(r'(\w+[^\s]\w+\s+\w+\s+\w+[^s+]суду)', i).group(1)
        container.append(m)  

    df['Суд'] = container
    
    reason = [ re.search(r'(\w+\s+\w+\s+\w+$)', i).group(1) for i in df['Назва документу'] ] 
    df['Підстава для звільнення'] = [' '.join(i.split(' ')[1:]) if 'у відставку' in i else i for i in reason]
    df['paste'] = df['Дата прийняття'].str.cat(df['Link'], sep='| ')
    return df[['id', 'Піб', 'Суд', 'Дата прийняття', 'Link', 'Підстава для звільнення', 'paste']]

if __name__ == "__main__":
    # якщо довго не перевіряти список звільнених
    page = sys.argv[1]
    url = 'http://www.vru.gov.ua/act_list' if page == 1 else 'http://www.vru.gov.ua/act_list/page/25?'
    try:
        df = parse_vrp(url=url)
        df = filter_data(df)
        df = add_info(df)
        df.to_excel(f"fired/звільн_онов_{str(datetime.datetime.now().date())}.xlsx", index=False)
    except:
        print("""1: перша сторінка,
        2: друга сторінка
        Наприклад, 
        "python ./fired.py 2"
        """)
    