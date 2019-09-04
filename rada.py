"""
# TO-DO:
1. написати скрипт, який буде зчитувати заголовки законопроектів [є, 17:57]
// написати скрипт для зчитування заголовків надходжень законопроетів? pd.read_html
2. визначити, за яким ключовим словом ідентифікувати потрібні законопроекти
3. перевірити, чи правильно було ідент. через додатковий запит в Картку Законопроекту
4. якщо правильно, відправити повідомлення на пошту 
5. додати якийсь scheduler 

Початок : 17:10, 04.09.2019
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd 

def read_news(url:str = 'https://rada.gov.ua/news/zp') -> pd.DataFrame:
    """Отримує номер, назву та лінк законопроектів з новинного фіду"""

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    
    text = [i.text for row in soup.select('#list_archive > div') for i in row.select('p')]
    link = [i['href'] for row in soup.select('#list_archive > div') for i in row.select('span > a')]

    return pd.DataFrame({'номер': text[::2], 'назва': text[1::2], 'лінк': link})

def read_nadhodzhennia(url:str) -> pd.DataFrame:
    # pd.read_html('http://w1.c1.rada.gov.ua/pls/zweb2/webproc555', encoding='cp1251')[0].head()
    pass

def bill_identifier(df: pd.DataFrame) -> pd.DataFrame:
    pass

def send_email():
    pass

def scheduler():
    pass