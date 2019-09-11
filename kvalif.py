import re, sys

import requests
from lxml.html import fromstring
from bs4 import BeautifulSoup

import pandas as pd


def parse_kvalif(url: str, file_name: str):
    """Парсер результатів кваліфоцінювання."""

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    lh_container = fromstring(soup.prettify())
    date_string = lh_container.xpath(
        "/html/body/div[1]/div/div[2]/div/div/div/div[1]/div/p[1]/text()"
    )
    date = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", " ".join(date_string)).group(1)

    df = pd.read_html(soup.prettify(), skiprows=1)[0]
    df.columns = ["ПІБ", "Суд", "К-сть балів", "Результат"]

    df["Дата кваліфоцінювання"] = date
    df["Результат"] = df["Результат"].str.split(".").str[0]
    df["Область"] = df["Суд"].str.split().str[-2:].str.join(" ")

    df["Чи є профайл"], df["Порушення доброчесності"], df["Дата відправки до ВККС"] = (
        "xxx",
        "xxx",
        "xxx",
    )
    df = df[
        [
            "Дата кваліфоцінювання",
            "ПІБ",
            "Область",
            "Чи є профайл",
            "Порушення доброчесності",
            "Дата відправки до ВККС",
            "Результат",
        ]
    ]
    df.to_excel(f"{file_name}.xlsx", sheet_name=f"{date}", index=False)


if __name__ == "__main__":
    args = sys.argv[1:]
    url, file_name = (args[0], args[1])
    parse_kvalif(url=url, file_name=file_name)
