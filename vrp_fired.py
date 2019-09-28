import os 
import sys 
import datetime

import numpy as np
import pandas as pd

import requests
from bs4 import BeautifulSoup

from concat_files import concat_files


def parse_vrp(url: str) -> pd.DataFrame:
    """Отримує дані з сторінки актів врп"""

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")

    records = []
    columns = []
    for tr in table.find_all("tr"):
        ths = tr.find_all("th")
        if ths != []:
            for each in ths:
                columns.append(each.text)
        else:
            trs = tr.find_all("td")
            record = []
            for each in trs:
                try:
                    link = each.find("a")["href"]
                    text = each.text
                    record.append(link)
                    record.append(text)
                except:
                    text = each.text
                    record.append(text)
            records.append(record)

    columns.insert(1, "Link")
    return pd.DataFrame(data=records, columns=columns)


def filter_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Відфільтровує звільнених, отримує імена, назви судів, підстави звільнення
    """

    df = dataframe.copy()
    df = df.loc[df["Назва документу"].str.contains("^Про звільнення")]
    df["Піб"] = df["Назва документу"].str.extract(r"(\w+\s\w\.\w\.)")
    df["Суд"] = df["Назва документу"].str.extract(
        r"(\w+\s+\w+\s+\bсуд[у]?\b\s+\w+\s+\w+)"
    )

    df["Підстава для звільнення"] = np.where(
        df["Назва документу"].str.contains("на підставі"),
        df["Назва документу"].str.extract(r"(\bна підставі\b.*)", expand=False),
        df["Назва документу"].str.extract(r"(\w+\s+\w+$)", expand=False),
    )

    df["paste"] = df["Дата прийняття"].str.cat(df["Link"], sep="| ")
    df["id"] = "xxxxx"
    df = df[
        [
            "id", "Піб", "Суд", "Дата прийняття",
            "Link", "Підстава для звільнення", "paste",
        ]
    ]
    return df[::-1]


if __name__ == "__main__":

    os.makedirs("./звільнення/", exist_ok=True)
    page = sys.argv[1]

    d = {}
    for i, j in zip(range(1, 31, 1), range(0, 775, 25)):
        d[str(i)] = str(j)

    for key, value in d.items():
        page = page.replace(key, value)


    url = f"http://www.vru.gov.ua/act_list/page/{page}?"
    df = parse_vrp(url)
    df = filter_data(df)
    df.to_excel(
            f"./звільнення/оновлено_{str(datetime.datetime.now().date())}.xlsx", index=False
    )

    concat_files()