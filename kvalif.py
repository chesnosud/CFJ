import sys, re
import requests
import pandas as pd
import lxml.html as LH
from bs4 import BeautifulSoup

def parse_kvalif(url: str, file_name: str):
    """Парсер результатів кваліфоцінювання."""
    
    # Отримую дату проведення кваліфу за допомогою regex
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    lh_container = LH.fromstring(soup.prettify())
    date_string = lh_container.xpath('/html/body/div[1]/div/div[2]/div/div/div/div[1]/div/p[1]/text()')
    date = re.search(r'([0-9]{1,2}\s+\w+\s+[0-9]{4})', ' '.join(date_string)).group(1)
    
    # Отримую таблицю з результатами та створюю нові колонки
    df = pd.read_html(soup.prettify(), skiprows=1)[0]
    df.columns = ['ПІБ', 'Суд', 'К-сть балів', 'Результат']
    df['Дата кваліфоцінювання'] = date
    df['Результат'] = [ i.split('.')[0] for i in df['Результат'] ]
    df['Чи є профайл'], df['Порушення доброчесності'], df['Дата відправки до ВККС']  = " ", " ", " "
    df = df[['Дата кваліфоцінювання', 'ПІБ', 'Суд', 'Чи є профайл', 'Порушення доброчесності', 'Дата відправки до ВККС', 'Результат']]
    df.to_excel(f"{file_name}.xlsx", sheet_name=f'{date}', index=False)

if __name__ == "__main__":
    args = sys.argv[1:]
    try:
        url, file_name = (args[0], args[1])
        parse_kvalif(url=url, file_name=file_name)
    except:
        print("""Були задані хибні аргументи
        Перший аргумент: url посилання на новину ВККС
        Другий агрумент: назва файлу для збереження результатів
        Де аргументи задані через один пробіл
        Наприклад, "python ./kvalif.py https://vkksu.gov.ua/ua/news/xxx kvalif_excel"
        """)