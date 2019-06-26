import requests, re
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
    df
    return df[::-1]

def add_info(df):
    """З тексту отримую назву суду та підставу для звільнення."""

    container = []
    reason = []
    for i in df['Назва документу']:
        try:
            m = re.search(r'(\w+[^\s]\w+\s\w+\s\суду\s\w+\s\w+)', i).group(1)
        except:
            m = re.search(r'(\w+[^\s]\w+\s+\w+\s+\w+[^s+]суду)', i).group(1)

        container.append(m)  
        reason.append(re.search(r'(\w+\s+\w+\s+\w+$)', i).group(1))
        
    df['Суд'] = container

    n = []
    for i in reason:
        if 'у відставку' in i:
            n.append(' '.join(i.split(' ')[1:]))
        else:
            n.append(i)
    df['Підстава для звільнення'] = n
    
    return df[['id', 'Піб', 'Суд', 'Дата прийняття', 'Link', 'Підстава для звільнення']]

if __name__ == "__main__":
    df = requests_beautifulsoup()
    df = filter_data(df)
    df = add_info(df)
    df.to_excel(f"zvilnenii.xlsx", sheet_name=f'test_26.06.2019')