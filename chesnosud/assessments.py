import re
import click
import requests
import numpy as np
import pandas as pd
from pathlib import Path
from lxml.html import fromstring
from tools import concat_files


PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "assessments"


@click.command()
@click.argument("link")
@click.option(
    "--concatenate", 
    prompt="Merge all files into one: [yes/no]",
    default="no", 
    help="Merges all files into one"
)
def get_results(link, concatenate) -> None:
    """ Read assessment results, change them according to the template, and save as .xlsx """  

    r = requests.get(link)

    date_string = fromstring(r.content).xpath(
        "/html/body/div[1]/div/div[2]/div/div/div/div[1]/div/p[1]/text()"
    )
    date = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", " ".join(date_string)).group(1)

    df = pd.read_html(r.content, skiprows=1)[0]
    df.columns = ["ПІБ", "Суд", "К-сть балів", "Результат"]

    df["Дата кваліфоцінювання"] = date 
    df["Результат"] = df["Результат"].str.split(".").str[0] # скорочений результат
    df["Область"] = np.where(
        df["Суд"].str.contains("адміністративний"), # якщо `адміністративний` суд
        df["Суд"].str.split().str[0], # то взяти перше слово
        df["Суд"].str.split().str[-2:].str.join(" ") # якщо ні, то останні два
    )
    df["Чи є профайл"], df["Порушення доброчесності"], df["Дата відправки до ВККС"] = (
        "xxx", "xxx", "xxx",
    )
    df = df[[
        "Дата кваліфоцінювання", "ПІБ", "Область", "Чи є профайл",
        "Порушення доброчесності", "Дата відправки до ВККС", "Результат",
    ]]

    # збереження таблиці в xlsx форматі
    df.to_excel(PATH / f"{date}_assessment.xlsx", index=False)

    if concatenate.lower().startswith("y"):
        concat_files(PATH, "*_assessment.xlsx")


if __name__ == "__main__":
    get_results()
