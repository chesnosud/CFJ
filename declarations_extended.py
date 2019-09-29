import os
from time import sleep
from typing import Dict, Iterator, List, Union

import requests
import pandas as pd
from pandas.io.json import json_normalize

from declarations_links import reshape_dataframe, rm_datedups


def step(
    data: List[dict], 
    step: str,
    columns_list: List[str] = ["objectType", "sizeIncome"],
    gifts: bool = False,
) -> Iterator[int]:
    """ 
    Повертає значення ключа step_n
    
    
    Parameters
    ----------
    data : list of dictionaries 
        є "i" елементом в r["results"]["object_list"][i]
    step : str
        вказує на поле, що містить необхідну інформацію.
         step_3: нерухоме майно, 
         step_6: рухоме майно, 
        step_11: дохід.
    columns_list : list of strings, default '["objectType", "sizeIncome"]' 
        змістовно насичені колонки, які слід лишити після створення табл.
        кожен step має окремі унікальні поля.
    gifts : bool, default False
        Якщо True, обмежує таблицю лише до тих значень, що типом доходу
        вказують "Подарунок ...", і повертає кількість подарунків у декл. 


    Examples
    --------
    >>> [sum(step(d, "step_3", ["objectType", "owningDate"])) for d in data)]
    1
    >>> [sum(step(d, "step_6", ["brand", "owningDate"])) for d in data]
    2
    >>> [sum(step(d, "step_11", gifts=True)) for d in data]
    3
    """

    try:
        for value in data["unified_source"][step].values():
            df = json_normalize(value)[columns_list]
            if gifts:
                yield len(df.loc[df["objectType"].str.contains("Подарунок")])
            else:
                yield len(df)
    except KeyError: # коли контейнер step відсутній; напр, декл. за 2014 або форми змін
        yield 0


def create_dataframe(data: List[Dict[str, Dict[str, Union[str, int]]]]) -> pd.DataFrame:
    """ 
    Створює таблицю на основі напівструктурованих даних, 
    отриманих з відкритого АРІ declarations.com.ua
    
    Основа таблиці формується зі слованика ["infocard"],
    колонки ["gift_num", "property_num", "vehicle_num"] - за допомогою генератора step.
    

    Parameters
    ----------
    data : list of nested dictionaries with either str or int values
        під data мається на увазі r["results"]["object_list"].


    Examples
    --------
    >>> df = create_frame(r["results"]["object_list"])
    >>> df.shape
    (n, 16)
    """

    data_container = []
    raw_source = []
    for i in range(len(data)):
        data_container.append(json_normalize(data[i]["infocard"]))

        try:
            rs = data[i]["raw_source"]["url"]
        except KeyError: # якщо декларація < 2015
            rs = data[i]["raw_source"]["declaration"]["url"]

        raw_source.append(rs)

    df = pd.concat(data_container, sort=True, ignore_index=True)
    df["link"] = raw_source
    df["gift_num"] = [sum(step(d, "step_11", gifts=True)) for d in data]
    df["property_num"] = [
        sum(step(d, "step_3", ["objectType", "owningDate"])) for d in data
    ]
    df["vehicle_num"] = [sum(step(d, "step_6", ["brand", "owningDate"])) for d in data]

    return df


def save(df: pd.DataFrame, person: str) -> None:
    """
    Змінює форму таблиці та записує результат в .xlsx файл


    Parameters
    ----------
    df : pd.DataFrame
        очищена фінальна таблиця, форму якої слід змінити та зберегти
    person : str
        ПІБ декларанта, яке використовується як назва файлу
    """

    df['paste'] = df["declaration_year"].astype(str).str.cat(df["link"], sep="| ")
    df = df[["paste", 'gift_num', "property_num", "vehicle_num"]]
    df.columns = ["Скопіювати", "Подарунок", "Нерухоме майно", "Рухоме майно"]
    df.to_excel(f"./декларації/{person}.xlsx", index=False)


if __name__ == "__main__":

    os.makedirs("./декларації/", exist_ok=True)

    with open("names.txt", encoding="utf-8") as file:
        names_list = file.read().splitlines()

    for person in names_list:
        try:
            url = f"http://declarations.com.ua/search?q={person}+AND+суддя&deepsearch=on&format=opendata"
            r = requests.get(url, sleep(0.5)).json()

            dataframe = create_dataframe(r["results"]["object_list"])
            reshaped_df = reshape_dataframe(dataframe, person)
            df = rm_datedups(reshaped_df)
            
            if df.empty:
                raise ValueError
            else:
                save(df, person)

        except ValueError:
            with open("./декларації/не_отримані.txt", "a") as ve:
                ve.write(f"{person}\n")
