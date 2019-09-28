import os
import sys
import re

import requests
from lxml.html import fromstring
from bs4 import BeautifulSoup

import pandas as pd

from concat_files import concat_files


def parse_kvalif(url: str) -> None:
    """ Парсить html таблицю з результати оцінювання
    
    url: посилання на новину 
    """

    # Отримання вмісту сторінки за url посиланням
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")

    # Отримання дати оцінювання за xpath тексту сторінки
    date_string = fromstring(soup.prettify()).xpath(
        "/html/body/div[1]/div/div[2]/div/div/div/div[1]/div/p[1]/text()"
    )
    date = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", " ".join(date_string)).group(1)

    # Зчитування html таблиці з результатами оцінювання
    df = pd.read_html(soup.prettify(), skiprows=1)[0]
    df.columns = ["ПІБ", "Суд", "К-сть балів", "Результат"]

    # Редагування таблиці 
    df["Дата кваліфоцінювання"] = date # додана дата оцінювання
    df["Результат"] = df["Результат"].str.split(".").str[0] # скорочений результат
    df["Область"] = df["Суд"].str.split().str[-2:].str.join(" ") # область з назви суду
    df["Чи є профайл"], df["Порушення доброчесності"], df["Дата відправки до ВККС"] = (
        "xxx", "xxx", "xxx",
    )
    df = df[
        [
            "Дата кваліфоцінювання", "ПІБ", "Область", "Чи є профайл",
            "Порушення доброчесності", "Дата відправки до ВККС", "Результат",
        ]
    ]
    
    # створення папки, в яку буде збережений результат
    os.makedirs("./результати_кваліфоцінювання", exist_ok=True)
    # збереження таблиці в xlsx форматі
    df.to_excel(
        f"./результати_кваліфоцінювання/{date}_результат.xlsx", 
        sheet_name=f"{date}", index=False)


if __name__ == "__main__":

    parse_kvalif(url=sys.argv[1])
    
    # об'єднує усі завантажені в папку файли в один
    concat_files(folder="результати_кваліфоцінювання")