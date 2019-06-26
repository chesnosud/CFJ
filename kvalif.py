import requests, re
import pandas as pd
import lxml.html as LH
from bs4 import BeautifulSoup

def kvalif(url, file_name):
    """Парсер результатів кваліфоцінювання.
          url: лінк на сторінку з результатами 
    file_name: назва файлу ексель, який буде створений
    """
    
    # Отримую дату проведення кваліфу за допомогою regex
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    lh_container = LH.fromstring(soup.prettify())
    date_string = lh_container.xpath('/html/body/div[1]/div/div[2]/div/div/div/div[1]/div/p[1]/text()')
    text = ''.join([ i for i in date_string ])
    pattern = r'([0-9]{2}.+[0-9]{4})'
    match = re.search(pattern, text)
    date = match.group(1)
    
    # Отримую таблицю з результатами та створюю нові колонки
    df = pd.read_html(url, decimal=',', skiprows=1)[0]
    columns = ['ПІБ', 'Суд', 'К-сть балів', 'Результат']
    df.columns = columns
    df['Дата кваліфоцінювання'] = date
    results = [ i.split('.')[0] for i in list(df['Результат']) ]
    df['Результат'] = results
    df.drop(['К-сть балів'], axis=1, inplace=True)
    df['Чи є профайл'] = "123"
    df['Порушення доброчесності'] = "123"
    df['Дата відправки до ВККС'] = "123"
    df = df[['Дата кваліфоцінювання', 'ПІБ', 'Суд', 'Чи є профайл', 'Порушення доброчесності', 'Дата відправки до ВККС', 'Результат']]
    
    df.to_excel(f"{file_name}.xlsx", sheet_name=f'{date}')

if __name__ == "__main__":
    url = 'https://vkksu.gov.ua/ua/news/xx-xxxxxx-xxxxxxx-xxxxxx-xxxxxx-xxxxxxxxxxxx-xxxxxxxx-xxxxxxxx'
    kvalif(url=url, file_name='kvalif')