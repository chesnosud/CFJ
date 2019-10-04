""" 
Отримує акти, що стосуються звільнень, та зберігає їх в .xlsx файл

Приклад використання: 
`python hcj_fired.py PAGE`
де PAGE є номером сторінки, напр. 1
"""

import os
import sys
import datetime

import pandas as pd

import requests
from bs4 import BeautifulSoup

from vrp_fired import filter_data
from concat_files import concat_files


def parse_page(page: str) -> pd.DataFrame:
    """ 
    Створює таблицю актів  
    
    Parameters
    ----------
    page : int
        Номер сторінки, з якої слід отримати таблицю
    """

    # отримання основного вмісту таблиці
    r = requests.get(f"http://hcj.gov.ua/acts?page={page}")
    soup = BeautifulSoup(r.text, "html.parser")
    df = pd.read_html(soup.prettify())[0]

    # отримання посилань на оригінал документів
    base_url, path = "http://hcj.gov.ua", "td.views-field.views-field-field-title > a"
    df["Link"] = [base_url + row["href"] for row in soup.select(path)]

    return df


if __name__ == "__main__":
    
    os.makedirs("./звільнення/", exist_ok=True)
    page = int(sys.argv[1]) - 1

    df = parse_page(page)
    df = filter_data(df)
    df.to_excel(
        f"звільнення/оновлено_{str(datetime.datetime.now().date())}.xlsx", index=False
    )

    concat_files(folder="звільнення")
