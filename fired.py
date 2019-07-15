import datetime, re
import requests
import pandas as pd
import lxml.html as LH
from bs4 import BeautifulSoup
from scrape import requests_beautifulsoup

def filter_data(dataframe):
    """
    Відбираю з отриманих результатів ті, що стосуються звільнень; 
    отримую з тексту ім'я;
    в результаті додаю нові колонки.
    """

    df = dataframe.copy()
    df = df.loc[df['Назва документу'].str.contains('звільн', case=False)]
    df = df.loc[~df['Назва документу'].str.contains('залишення без розгляду', case=False)]
    df['Піб'] = [ re.search(r'(\w+\s\w\.\w\.)', n).group(1) for n in list(df['Назва документу']) ]
    df['id'] = 'xxxxx'
    df['Суд'] = 'xxxxx'
    df = df[['id', 'Піб', 'Суд', 'Дата прийняття', 'Link', 'Назва документу']]
    return df[::-1]

def add_info(df):
    """З тексту отримую назву суду та підставу для звільнення."""

    df['Filter'] = df['Назва документу'].str.contains('суду', regex=True)
    df = df.loc[df['Filter'].eq(True)]
    
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
    df = requests_beautifulsoup(url='http://www.vru.gov.ua/act_list')
    df = filter_data(df)
    df = add_info(df)
    date = datetime.datetime.now().date()
    df.to_excel(f"fired/звільн_онов_{str(date)}.xlsx", sheet_name=f'оновл. {str(date)}')