import os
import sys
import datetime

import pandas as pd

import requests
from bs4 import BeautifulSoup

from vrp_fired import filter_data
from concat_files import concat_files


def parse_page(url: str) -> pd.DataFrame:
    """ Парсить таблицю з нового сайту """

    # отримання основного вмісту таблиці
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    df = pd.read_html(soup.prettify())[0]

    # отримання посилань на оригінал документів
    base_url, path = "http://hcj.gov.ua", "td.views-field.views-field-field-title > a"
    df["Link"] = [base_url + row["href"] for row in soup.select(path)]

    return df


if __name__ == "__main__":
    
    os.makedirs("./звільнення/", exist_ok=True)
    page = str(int(sys.argv[1]) - 1)

    url = f"http://hcj.gov.ua/acts?page={page}"

    df = parse_page(url)
    df = filter_data(df)
    df.to_excel(
        f"звільнення/оновлено_{str(datetime.datetime.now().date())}.xlsx", index=False
    )

    concat_files(folder="звільнення")
