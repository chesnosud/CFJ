import requests, re, sys
import pandas as pd
from lxml.html import fromstring
from bs4 import BeautifulSoup

def parse_kvalif(url: str, file_name: str):
    """Парсер результатів кваліфоцінювання."""
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    lh_container = fromstring(soup.prettify())
    date_string = lh_container.xpath('/html/body/div[1]/div/div[2]/div/div/div/div[1]/div/p[1]/text()')
    date = re.search(r'([0-9]{1,2}\s+\w+\s+[0-9]{4})', ' '.join(date_string)).group(1)
    
    df = pd.read_html(soup.prettify(), skiprows=1)[0]
    df.columns = ['ПІБ', 'Суд', 'К-сть балів', 'Результат']
    df['Дата кваліфоцінювання'] = date
    df['Результат'] = [ i.split('.')[0] for i in df['Результат'].values.tolist() ]
    df['Чи є профайл'], df['Порушення доброчесності'], df['Дата відправки до ВККС']  = " ", " ", " "
    df['Область'] = [i.split()[-2:] for i in df['Суд'].values.tolist()]
    df['Область'] = df['Область'].str.join(' ')
    df = df[['Дата кваліфоцінювання', 'ПІБ', 'Область', 'Чи є профайл', 'Порушення доброчесності', 'Дата відправки до ВККС', 'Результат']]
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
        Наприклад, "python ./kvalif.py https://vkksu.gov.ua/ua/news/xxx 19-липня"
        """)