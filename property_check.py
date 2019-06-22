""" Перевірка об'єктів нерухомості в деклараціях

# TO DO:
* визначити, як саме порівняти таблиці (поки думав про `df1.equals(df2)`)
* зробити таке ж саме для автівок

@hp0404, 23.06.2019
"""

import pandas as pd

def get_property(url):
    df = pd.read_html(url, match='Загальна інформація')
    return df[0]

def clean_property(df):
    """Форматування таблиці. 
    type df: pd.DataFrame();  
    """

    def function_vyd(i):
        """Змінюю str у колонці "Вид об'єкта" залежно від умов."""

        v = i[0].split(':')[-1]
        if ',' in v:
            vyd_modified = v.split(',')[0]
            return vyd_modified
        else:
            return v
        
    # function_vyd = lambda i: i[0].split(':')[-1].split(',')[0] if ',' in i[0].split(':')[-1] else i[0].split(':')[-1]
    
    # визначаю, які колонки слід розділити та за якою ознакою
    info = df['Загальна інформація'].str.split('\xa0')
    location = df['Місцезнаходження'].str.split('\xa0')
    
    # в межах визначених колонок змінюю значення 
    vyd = [function_vyd(i) for i in info]
    date = [i[1].split(':')[-1] for i in info]
    sqm = [i[2].split(' ')[-1] for i in info]
    city = [i[2].split(':')[-1] for i in location]
    price = list(df['Вартість на дату набуття'])
    
    # додаю усі нові змінні в контейнер та створюю headers для DataFrame
    containers = [vyd, date, sqm, city, price]
    columns=["Вид об'єкта", "Дата набуття права", "Загальна площа", "Місто", "Вартість"]
    
    # створюю DataFrame з контейнера
    dataframe = pd.DataFrame.from_records(containers).T
    dataframe.columns = columns
    
    return dataframe


if __name__ == "__main__":
    url = 'https://public.nazk.gov.ua/declaration/6c2d033d-48b7-435c-a768-a0a029880f57'
    raw_df = get_property(url)
    df = clean_property(raw_df)