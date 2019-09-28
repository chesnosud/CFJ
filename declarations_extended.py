import os
from time import sleep
from typing import List

import requests
import pandas as pd
from pandas.io.json import json_normalize

from declarations_links import reshape_dataframe, rm_datedups


def step(
    data: List[dict],
    step: str,
    columns_list=["objectType", "sizeIncome"],
    present=False,
):
    """
    """

    try:
        for value in data["unified_source"][step].values():
            df = json_normalize(value)[columns_list]
            if present:
                yield len(df.loc[df["objectType"].str.contains("Подарунок")])
            else:
                yield len(df)
    except KeyError:
        yield 0


def create_dataframe(r: dict) -> pd.DataFrame:

    path = r["results"]["object_list"]
    data_container = []
    raw_source = []
    for i in range(len(path)):
        data_container.append(json_normalize(path[i]["infocard"]))

        try:
            rs = path[i]["raw_source"]["url"]
        except KeyError:
            rs = path[i]["raw_source"]["declaration"]["url"]

        raw_source.append(rs)

    df = pd.concat(data_container, sort=True, ignore_index=True)
    df["link"] = raw_source
    df["present_num"] = [sum(step(d, "step_11", present=True)) for d in path]
    df["property_num"] = [
        sum(step(d, "step_3", ["objectType", "owningDate"])) for d in path
    ]
    df["vehicle_num"] = [sum(step(d, "step_6", ["brand", "owningDate"])) for d in path]

    return df


def save(df, person):

    df['paste'] = df["declaration_year"].astype(str).str.cat(df["link"], sep="| ")
    df = df[["paste", 'present_num', "property_num", "vehicle_num"]]
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
            df = rm_datedups(reshape_dataframe(create_dataframe(r), person))
            
            if df.empty:
                raise ValueError
            else:
                save(df, person)
        except ValueError:
            with open("./декларації/не_отримані.txt", "a") as ve:
                ve.write(f"{person}\n")
