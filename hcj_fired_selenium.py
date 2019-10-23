import os
import sys
import datetime

import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from vrp_fired import filter_data
from concat_files import concat_files


def parse_selenium(page) -> pd.DataFrame:
    """ 
    Створює таблицю актів  
    
    Parameters
    ----------
    page : int
        Номер сторінки, з якої слід отримати таблицю
    """

    url = f"http://hcj.gov.ua/acts?page={page}"

    options = Options()
    options.headless = True
    
    with webdriver.Chrome("./chromedriver.exe", options=options) as browser:
        browser.get(url)
        html = browser.page_source
        
    soup = BeautifulSoup(html, "html.parser")
    df = pd.read_html(soup.prettify())[0]
    
    base_url, path = "http://hcj.gov.ua", "td.views-field.views-field-field-title > a"
    df["Link"] = [base_url + row["href"] for row in soup.select(path)]

    return df 


if __name__ == "__main__":
    
    os.makedirs("./звільнення/", exist_ok=True)
    page = int(sys.argv[1]) - 1

    df = parse_selenium(page)

    try:
        df = filter_data(df)
        df.to_excel(
            f"звільнення/оновлено_{str(datetime.datetime.now().date())}.xlsx", 
            index=False
        )
        concat_files(folder="звільнення")
    except ValueError:
        print("Звільнених на цій сторінці немає")