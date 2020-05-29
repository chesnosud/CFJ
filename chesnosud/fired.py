import click
import requests
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tools import concat_files


PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "fired"
URL_HCJ = "http://hcj.gov.ua/acts"
URL_VRP = "http://www.vru.gov.ua/act_list/page/" 
VRP_MAX_PAGES = 775
VRP_PAGES = {
    user_page:site_page
    for user_page, site_page in 
    zip(range(1,50+1), range(0, VRP_MAX_PAGES, 25))
}
UA = UserAgent()
DATE = datetime.today().strftime("%Y-%m-%d")


def parse_vrp(page: str) -> pd.DataFrame:
    """Отримує дані з сторінки актів врп"""

    response = requests.get(URL_VRP + str(page), headers={"User-Agent": UA.random})
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


def parse_hcj(page: str) -> pd.DataFrame:
    """ 
    Створює таблицю актів  
    
    Parameters
    ----------
    page : int
        Номер сторінки, з якої слід отримати таблицю
    """

    # отримання основного вмісту таблиці
    r = requests.get(URL_HCJ, params={"page": page}, headers={"User-Agent": UA.random})
    soup = BeautifulSoup(r.text, "html.parser")
    df = pd.read_html(soup.prettify())[0]

    # отримання посилань на оригінал документів
    base_url, path = "http://hcj.gov.ua", "td.views-field.views-field-field-title > a"
    df["Link"] = [base_url + row["href"] for row in soup.select(path)]

    return df


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


@click.command()
@click.option("--site", prompt="Site: [vrp/hcj]", default="vrp",help="Two official sites are vrp and hcj")
@click.option("--page", prompt="Page:", default=1, help="Page number")
@click.option("--concatenate", prompt="Merge all files into one: [yes/no]",
              default="no", help="Merges all files into one")
def cli(site, page, concatenate):
    """Create a table of fired judges for given page on either of two official sites."""
    
    if site.lower() == "vrp":
        data = parse_vrp(VRP_PAGES.get(page)) 
    else:
        data = parse_hcj(page-1)
        
    df = filter_data(data)
    
    name = f"{DATE}_fired.xlsx"
    df.to_excel(PATH / name, index=False)
    
    if concatenate.lower().startswith("y"):
        concat_files(PATH, "*_fired.xlsx")
        

if __name__ == "__main__":
    cli()
    