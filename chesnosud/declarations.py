import click
import requests
import pandas as pd
from time import sleep
from pathlib import Path
from typing import Any, Dict, Iterable, List


PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "declarations"


def count_gifts(data: List[Any]) -> Iterable[int]:
    """ Перевіряє наявність подарунків в декларації та повертає розмір кожної. 
    

    Parameters
    ----------
    data : list of nested dictionaries (requests' response)
        Є аргументом генератора `step`.   
    """
    for income_type in data.values():
        if "Подарунок" in income_type["objectType"]:
            yield income_type["sizeIncome"]


def step(data: List[Any]) -> Iterable[Dict[str, int]]:
    """ Збирає інформацію, що стосується (не)рухомого майна та подарунків судді.
    

    Parameters
    ----------
    data : list of nested dictionaries (requests' response)
        Відповідь declarations.com API


    Notes
    -----
    Expected exceptions:
    KeyError
        Коли ключ відсутній (відсутнє майно або подарунки), повертає 0;    
     """

    for item in data:

        step = item["unified_source"]

        try:
            url = item["raw_source"]["url"]
        except KeyError:
            url = item["raw_source"]["declaration"]["url"]
        try:
            gifts = list(count_gifts(step["step_11"]))
        except KeyError:
            gifts = False

        step_3, step_6 = step.get("step_3"), step.get("step_6")

        yield {
            "link": url,
            "property_num": len(step_3) if step_3 else 0,
            "vehicle_num": len(step_6) if step_6 else 0,
            "gift_num": len(gifts) if gifts else 0,
            "gift_sum": sum(gifts) if gifts else 0,
        }


def create_dataframe(data: List[Any]) -> pd.DataFrame:
    """Створює таблицю на основі напівструктурованих даних АРІ declarations.com.ua
    
    
    Parameters
    ----------
    data : list of nested dictionaries (requests' response)
        Відповідь declarations.com API.
    
    
    Notes
    -----
    Основа таблиці формується з поля `infocard`, додаткові відомості - майно, 
    подарунки, лінки - з полів `unified_source` та `raw_source` відповідно. 
    """

    df = pd.concat(
        [pd.json_normalize(item["infocard"]) for item in data], ignore_index=True
    )
    meta_data = pd.DataFrame(step(data))

    return df.join(meta_data)


def reshape_dataframe(dataframe: pd.DataFrame, name: str) -> pd.DataFrame:
    """Перероблює таблицю:
        (а) створює нові та прибирає зайві колонки;
        (б) верифікує декларанта;
        (в) позбувається 'Форм змін'
        
        
    Parameters
    ----------
    dataframe : pd.DataFrame
        Таблиця, отримана з create_dataframe().
    name: str
        ПІБ декларанта; використовується верифікації декларанта.
    """

    df = dataframe.copy()

    df["name"] = (
        df["last_name"]
        .str.cat(df["first_name"], sep=" ")
        .str.cat(df["patronymic"], sep=" ")
    )

    df = df.loc[(df["name"].eq(name)) & (df["document_type"].ne("Форма змін"))]

    useless_columns = [
        "first_name",
        "last_name",
        "patronymic",
        "id",
        "is_corrected",
        "position",
        "url",
    ]

    return df.drop(useless_columns, axis=1)


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
        pat="https://public-api.nazk.gov.ua/v1/declaration/",
        repl="https://public.nazk.gov.ua/declaration/",
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

    df["paste"] = df["declaration_year"].astype(str).str.cat(df["link"], sep="| ")
    df = df[["paste", "property_num", "vehicle_num", "gift_num", "gift_sum"]]
    df.columns = ["Скопіювати", "Нерухоме майно", "Рухоме майно", "Кількість подарунків", "Розмір усіх подарунків"]
    df.to_excel(PATH / f"{name}.xlsx", index=False)


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
def cli(input_path):
    """ Download declarations for given names. """
    with open(input_path, encoding="utf-8") as input_file:
        names_list = input_file.read().splitlines()

    for i, person in reversed(list(enumerate(names_list))):
        person = person.strip().partition(".")[0]
        url = f"http://declarations.com.ua/search?q={person}+AND+суддя&deepsearch=on&format=opendata"

        try:
            r = requests.get(url, sleep(0.5)).json()
            table = create_dataframe(r["results"]["object_list"])
            reshaped_df = reshape_dataframe(table, person)
            frame = rm_datedups(reshaped_df)

            if frame.empty:
                raise ValueError
            else:
                save(frame, person)

        except ValueError:
            with open(output_path, "a") as ve:
                ve.write(f"{person}\n")

        
        click.echo(f"{i}, {person}")


if __name__ == "__main__":
    cli()
