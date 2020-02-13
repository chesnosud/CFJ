import os
import sys
import re

import requests
from lxml.html import fromstring

import numpy as np
import pandas as pd

from concat_files import concat_files


def get_results(url: str) -> None:
    """ 
    Опрацьовує результати кваліфоцінювання:
        (а) отримує html таблицю з результатами;
        (б) змінює її відповідно до шаблону;
        (в) зберігає як .xlsx файл 
    
    Parameters
    ----------
    url : str
        Посилання на новину
    """

    # Отримання вмісту сторінки за url посиланням
    r = requests.get(url)

    # Отримання дати оцінювання за xpath тексту сторінки
    date_string = fromstring(r.content).xpath(
        "/html/body/div[1]/div/div[2]/div/div/div/div[1]/div/p[1]/text()"
    )
    date = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", " ".join(date_string)).group(1)

    # Зчитування html таблиці з результатами оцінювання
    df = pd.read_html(r.content, skiprows=1)[0]
    df.columns = ["ПІБ", "Суд", "К-сть балів", "Результат"]

    # Редагування таблиці 
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
    
    # створення папки, в яку буде збережений результат, якщо папки не існує
    os.makedirs("./результати_кваліфоцінювання", exist_ok=True)
    
    # збереження таблиці в xlsx форматі
    df.to_excel(
        f"./результати_кваліфоцінювання/{date}_результат.xlsx", 
        sheet_name=f"{date}", 
        index=False
    )


if __name__ == "__main__":

    # завантаження результатів
    get_results(url=sys.argv[1])
    
    # об'єднує усі завантажені в папку файли в один
    concat_files(folder="результати_кваліфоцінювання")