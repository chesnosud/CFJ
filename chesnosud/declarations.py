import logging
import click
import requests
import numpy as np
import pandas as pd
from time import sleep
from pathlib import Path
from typing import Any, Dict, Iterable, List


PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "declarations"


def count_things(
    data: Dict[str, Any], 
    value_type: str = "gifts"
) -> Iterable[Any]:
    """ Перевіряє наявність "одиниці" в декларації та повертає розмір кожної. 
    

    Parameters
    ----------
    data : Dict[str, Any]
        requests' response: unified_source
        
    value_type : str
        Тип об'єкта, який слід перевірити (sizeIncome, model, totalArea)
    """
    for item in data.values():
        if value_type == "gifts":
            if "Подарунок" in item["objectType"]:
                yield item["sizeIncome"]
        else:
            yield item.get(value_type, 0)
            
            
def step(data: List[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
    """ Збирає інформацію, що стосується (не)рухомого майна та подарунків декларанта.
    

    Parameters
    ----------
    data : List[Dict[str, Any]]
        requests' response: object_list and raw_source


    Notes
    -----
    Expected exceptions:
    KeyError
        Коли ключ відсутній (відсутнє майно або подарунки), повертає 0 або "";    
     """
    for item in data:

        step = item["unified_source"]

        try:
            url = item["raw_source"]["url"]
        except KeyError:
            url = item["raw_source"]["declaration"]["url"]
        try:
            gifts = list(count_things(step["step_11"]))
        except KeyError:
            gifts = False
        
        try:
            area = list(count_things(step["step_3"], value_type="totalArea"))
        except KeyError:
            area = False
        
        try:
            vehicles = list(count_things(step["step_6"], value_type="model"))
        except KeyError:
            vehicles = False

        step_3, step_6 = step.get("step_3"), step.get("step_6")

        yield {
            "link": url,
            "real_estate": len(step_3) if step_3 else 0,
            "real_estate_area": sum(area) if area else 0,
            "vehicle_num": len(step_6) if step_6 else 0,
            "vehicle_models": "; ".join(str(v) for v in vehicles) if vehicles else "",
            "gift_num": len(gifts) if gifts else 0,
            "gift_sum": sum(gifts) if gifts else 0,
        }
        
        
def infocard(data: List[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
    """ Збирає інформацію, що стосується основний відомостей про декларанта
    
    
    Parameters
    ----------
    data : List[Dict[str, Any]]
        requests' response: infocard
    """
    for item in data:
        infocard = item["infocard"]
        name = f"{infocard['last_name']} {infocard['first_name']} {infocard['patronymic']}"
        
        yield {
            "name": name,
            "document_type": infocard["document_type"],
            "created_date": infocard["created_date"],
            "declaration_year": infocard["declaration_year"]
        }
    

def create_dataframe(
    data: List[Dict[str, Any]], 
    name: str
) -> pd.DataFrame:
    """Створює таблицю на основі напівструктурованих даних АРІ declarations.com.ua
    
    
    Parameters
    ----------
    data : List[Dict[str, Any]]
        requests' response: object_list
    
    name: str
        ПІБ декларанта; використовується верифікації декларанта.
    
    
    Notes
    -----
    Основа таблиці формується з поля infocard, додаткові відомості - майно, 
    подарунки, лінки - з полів unified_source та raw_source відповідно. 
    """
    table = pd.DataFrame(infocard(data))
    metadata = pd.DataFrame(step(data))
    df = table.join(metadata)
    
    return df.loc[(df["name"].eq(name)) & (df["document_type"].ne("Форма змін"))]


def rm_datedups(dataframe: pd.DataFrame) -> pd.DataFrame:
    """ Усуває подвоєні декларації.


    Parameters
    ----------
    dataframe : pd.DataFrame
        Отримана з reshape_dataframe() таблиця
    
    
    Notes
    -----
    Конвертує час подання декларації в datetime, що дозволяє
    відсортувати таблицю й залишити найактуальнішу декл. за звітній період;
    окремо позбувається парерової декларації за 2015 рік.
    Examples
    --------
    >>> df
            created_date	    declaration_year	link
    1	2019-03-20T00:00:00	    2018	            df67e
    5	2019-03-26T00:00:00	    2018	            d354c
    >>> rm_datedups(df)
            created_date	    declaration_year	link
    5	2019-03-26	            2018	            d354c
    """
    df = dataframe.copy()
    df["created_date"] = pd.to_datetime(
        df["created_date"], format="%Y-%m-%d", errors="coerce"
    )
    df["declaration_year"] = df["declaration_year"].astype(int)
    
    df = df.loc[~(df["declaration_year"].eq(2015) & df["link"].str.contains("/static"))]
    df = df.sort_values("created_date").drop_duplicates("declaration_year", keep="last")

    df["link"] = df["link"].str.replace(
        "https://public-api.nazk.gov.ua/v1/declaration/",
        "https://public.nazk.gov.ua/declaration/",
    )

    return df.sort_values("declaration_year")


def save(df: pd.DataFrame, name: str) -> None:
    """ Зберігає перетворену таблицю. 
    

    Parameters
    ----------
    df : pd.DataFrame
        очищена фінальна таблиця, форму якої слід змінити та зберегти
    name : str
        ПІБ декларанта, яке використовується як назва файлу
    """
    _columns = {
        "paste": "Скопіювати", 
        "real_estate": "Нерухоме майно",
        "real_estate_area": "Площа нерухомого майна",
        "vehicle_num": "Рухоме майно", 
        "vehicle_models": "Модель рухомого майна",
        "gift_num": "Кількість подарунків",
        "gift_sum": "Розмір усіх подарунків"
    }

    df["paste"] = df["declaration_year"].astype(str).str.cat(df["link"], sep="| ")
    df = df[list(_columns.keys())].rename(columns=_columns)
    df.to_excel(PATH / f"{name}.xlsx", index=False)
    

def collect_declarations(names: List[str], verbose : bool = False):
    """ Збирає декларації, повертає імена в разі помилки. 
    
    Parameters
    ----------
    names: List[str]
        Перелік ПІБ, чиї декларації слід зібрати
    """
    for i, person in reversed(list(enumerate(names))):
        person = person.strip().partition(".")[0]
        url = f"http://declarations.com.ua/search?q={person}+AND+суддя&deepsearch=on&format=opendata"

        try:
            r = requests.get(url, sleep(0.5)).json()
            data = r["results"]["object_list"]
            table = create_dataframe(data, person)
            result = rm_datedups(table)

            if result.empty:
                raise ValueError
            else:
                save(result, person)

        except ValueError:
            logging.info(person)
            
        
        if verbose and i != 0:
            click.echo(f"{i} left")


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Print more output.")
def cli(input_path, verbose):
    """ Download declarations for given names. """
    declarants = pd.read_excel(input_path)
    names = declarants["names"].to_list()
    collect_declarations(names, verbose)
        

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[
            logging.FileHandler(PATH / "declarations.log"),
            logging.StreamHandler()
        ]
    )

    cli()
