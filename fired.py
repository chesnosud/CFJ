import datetime, re
import requests
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
    df = df.loc[df['Назва документу'].str.contains('суду', regex=True)]
    df['Піб'] = [ re.search(r'(\w+\s\w\.\w\.)', n).group(1) for n in df['Назва документу'] ]
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
    return df[['id', 'Піб', 'Суд', 'Дата прийняття', 'Link', 'Підстава для звільнення']]

if __name__ == "__main__":
    df = parse_vrp(url='http://www.vru.gov.ua/act_list')
    df = filter_data(df)
    df = add_info(df)
    df.to_excel(f"fired/звільн_онов_{str(datetime.datetime.now().date())}.xlsx")