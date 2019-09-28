import os
from time import sleep

import requests
import pandas as pd
from pandas.io.json import json_normalize


def create_dataframe(r: dict) -> pd.DataFrame:
    """
    """

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

    return df


def reshape_dataframe(dataframe: pd.DataFrame, person: str) -> pd.DataFrame:
    """
    """

    df = dataframe.copy()

    df["name"] = (
        df["last_name"]
        .str.cat(df["first_name"], sep=" ")
        .str.cat(df["patronymic"], sep=" ")
    )

    df = df.loc[(df["name"].eq(person)) & (df["document_type"].ne("Форма змін"))]

    useless_columns = [
        "first_name", "last_name", "patronymic", "id", "is_corrected", "position", "url"
        ]

    return df.drop(useless_columns, axis=1)


def rm_datedups(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    """

    df = dataframe.copy()

    df["created_date"] = pd.to_datetime(
        df["created_date"], format="%Y-%m-%d", errors="coerce"
    )

    df["declaration_year"] = df["declaration_year"].astype(int)
    df = df.loc[~(df["declaration_year"].eq(2015) & df["link"].str.contains("/static"))]

    df = df.sort_values("created_date").drop_duplicates("declaration_year", keep="last")

    df["link"] = df["link"].str.replace(
        pat="https://public-api.nazk.gov.ua/v1/declaration/",
        repl="https://public.nazk.gov.ua/declaration/",
    )

    return df.sort_values("declaration_year")


def save(df: pd.DataFrame) -> None:
    """
    """
    paste = df["declaration_year"].astype(str).str.cat(df["link"], sep="| ")
    pd.DataFrame(paste).to_csv(f"./декларації/{person}.csv", index=False)


def main(person: str) -> None:
    """
    """

    url = f"http://declarations.com.ua/search?q={person}+AND+суддя&deepsearch=on&format=opendata"
    r = requests.get(url, sleep(0.5)).json()

    dataframe = create_dataframe(r)
    reshaped_df = reshape_dataframe(dataframe, person)
    df = rm_datedups(reshaped_df)

    if df.empty:
        raise ValueError
    else:
        save(df)


if __name__ == "__main__":

    os.makedirs("./декларації/", exist_ok=True)

    with open("names.txt", encoding="utf-8") as file:
        names_list = file.read().splitlines()

    for person in names_list:
        try:
            main(person)
        except ValueError:
            with open("./декларації/не_отримані.txt", "a") as ve:
                ve.write(f"{person}\n")
