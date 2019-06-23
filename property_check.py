""" Перевірка об'єктів нерухомості в деклараціях

# TO DO:
* визначити, як саме порівняти таблиці (поки думав про `df1.equals(df2)`)
* зробити таке ж саме для автівок [DONE]

@hp0404, 23.06.2019
"""

import pandas as pd

def get_property(url):
    """Отримую дані з декларації.
    
    property table: таблиця з нерухомим майном;
        cars_table: таблиця з рухомим майном.  
    """

    property_table = pd.read_html(url, match='Вартість на дату набуття')[0]
    cars_table = pd.read_html(url, match='Вартість на дату набуття у власність, володіння чи користування')[0]
    return property_table, cars_table

def clean_property(df):
    """Форматування таблиці. 
    type df: pd.DataFrame();  
    """
    
    def function_vyd(i):
        """Змінюю str у колонці "Вид об'єкта" залежно від типу."""
        v = i[0].split(':')[-1]
        if ',' in v:
            return v.split(',')[0]
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

def clean_cars(df):
    """Спрощення таблиці з рухомим майном.
    type df: pd.DataFrame();
    """
    
    # визначаю, які колонки слід розділити та за якою ознакою
    inf = df['Загальна інформація'].str.split('\xa0')
    char = df['Характеристика'].str.split('\xa0')
    
    # в межах визначених колонок змінюю значення 
    vyd = [i[0].split(':')[1] for i in inf]
    date = [i[1].split(':')[1] for i in inf]
    marka = [i[0].split(':')[-1] for i in char]
    model = [i[1].split(':')[-1] for i in char]
    year = [i[2].split(':')[-1] for i in char]
    price = list(df['Вартість на дату набуття у власність, володіння чи користування'])
    
    # додаю усі нові змінні в контейнер та створюю DataFrame
    data = [vyd, date, marka, model, year, price]
    dataframe = pd.DataFrame.from_records(data).T
    
    # колонки
    columns=["Вид об'єкта", "Дата набуття права", "Марка", "Модель", "Рік випуску", "Вартість"]
    dataframe.columns = columns
    
    return dataframe


if __name__ == "__main__":
    url = 'https://public.nazk.gov.ua/declaration/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
    prop_raw, cars_raw = get_property(url=url)
    prprty = clean_property(prop_raw)
    cars = clean_cars(cars_raw)