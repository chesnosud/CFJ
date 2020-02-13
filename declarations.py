import os
from time import sleep
from typing import Any, List, Iterable

import requests
import pandas as pd
from pandas.io.json import json_normalize


def step(
    data: Any, step_num: str, columns_list: List[str], gifts: bool = False
) -> Iterable[int]:
    """
    Повертає значення ключа step_n

    Parameters
    ----------
    data : list of nested dictionaries
        Є "i" елементом в r["results"]["object_list"][i];
        Кожен "i" елемент містить декілька випадково(?) згенерованих dict,
        які виглядають приблизно таким чином: Dict[str, Union[str, int]].
    step_num : str
        Вказує на поле, що містить необхідну інформацію.
         step_3: нерухоме майно,
         step_6: рухоме майно,
        step_11: дохід.
    columns_list : list of strings
        Змістовно насичені колонки, які слід лишити після створення табл.;
        кожен step_num має унікальні поля, тому їх слід щоразу вказувати
    gifts : bool, default 'False'
        Якщо True, обмежує таблицю лише до тих значень, що типом доходу
        вказують "Подарунок ...", і повертає кількість подарунків у декл.

    Yields
    ------
    int
        Повертає кількість чогось - об'єктів (не)рухомого майна; подарунків.

    Notes
    -----
    Початково функція отримувала суму річного доходу, але оскільки алгоритм для майже
    всіх step_num є однаковим, я переписав первинну ф-цію більш абстрактно.
    Якщо виникне потреба додати щось складніше, напевно напишу окремою ф-цією.

    В документації до цієї ф-ції відсутні Examples - див. застосування в create_dataframe().

    Очікувані exceptions:
    KeyError
        Коли контейнер step_num відсутній, повертає 0;
        Напр., у випадках з декл. за 2013-2014 рр. та у декл. "Форми змін"
    """

    try:
        for value in data["unified_source"][step_num].values():
            df = json_normalize(value)[columns_list]
            if gifts:
                yield len(df.loc[df["objectType"].str.contains("Подарунок")])
            else:
                yield len(df)
    except KeyError:
        yield 0


def create_dataframe(data: Any, detailed: bool = False) -> pd.DataFrame:
    """
    Створює таблицю на основі напівструктурованих даних АРІ declarations.com.ua

    Parameters
    ----------
    data : list of nested dictionaries
        Під data мається на увазі r["results"]["object_list"].
    detailed : bool, default 'False'
        Якщо True, звертається до генератора step та додає інформацію по статках

    Notes
    -----
    Основа таблиці формується з поля `infocard`,
    колонки `gift_num`, `property_num`, `vehicle_num` - за допомогою генератора step,
    `link` - з dict `raw_source`.
    Оскільки стуктура об'єкту складна, не можу правильно вказати його тип, - пишу Any.

    Очікувані exceptions:
    KeyError
        Коли шляху ["raw_source"]["url"] не існує, звертається до
        ["raw_source"]["declaration"]["url"];
        Трапляється з декл. 2013-2014 рр.

    Examples
    --------

    >>> df = create_dataframe(r["results"]["object_list"])
    >>> df.shape
    (n, 13)
    >>> df = create_dataframe(r["results"]["object_list"], detailed=True)
    >>> df.shape
    (n, 16)
    """

    data_container = []
    raw_source = []
    for i in range(len(data)):
        data_container.append(json_normalize(data[i]["infocard"]))

        try:
            rs = data[i]["raw_source"]["url"]
        except KeyError:
            rs = data[i]["raw_source"]["declaration"]["url"]
        raw_source.append(rs)

    df = pd.concat(data_container, sort=True, ignore_index=True)
    df["link"] = raw_source

    if detailed:
        df["gift_num"] = [
            sum(step(d, "step_11", ["objectType", "sizeIncome"], gifts=True)) for d in data
        ]
        df["property_num"] = [
            sum(step(d, "step_3", ["objectType", "owningDate"])) for d in data
        ]
        df["vehicle_num"] = [
            sum(step(d, "step_6", ["brand", "owningDate"])) for d in data
        ]

    return df


def reshape_dataframe(dataframe: pd.DataFrame, name: str) -> pd.DataFrame:
    """
    Перероблює таблицю:
        (а) створює нові та прибирає зайві колонки;
        (б) верифікує декларанта;
        (в) позбувається декларацій типу 'Форма змін'

    Parameters
    ----------
    dataframe : pd.DataFrame
        Таблиця; припускаю, що отримана з create_table().
    name: str
        ПІБ декларанта; використовується верифікації декларанта
        (реєстр іноді підтягує декларації з іншим ПІБ).

    Examples
    --------

    >>> reshaped_df = reshape_dataframe(dataframe)
    >>> reshaped_df.shape
    (n, 10)
    """

    df = dataframe.copy()

    df["name"] = (
        df["last_name"]
        .str.cat(df["first_name"], sep=" ")
        .str.cat(df["patronymic"], sep=" ")
    )

    df = df.loc[(df["name"].eq(name)) & (df["document_type"].ne("Форма змін"))]

    useless_columns = [
        "first_name", "last_name", "patronymic",
        "id", "is_corrected", "position", "url"
    ]

    return df.drop(useless_columns, axis=1)


def rm_datedups(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Усуває подвоєні декларації.

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


def save(df: pd.DataFrame, name: str, excel: bool = False) -> None:
    """
    Змінює форму таблиці та записує результат в .csv або .xlsx файл

    Parameters
    ----------
    df : pd.DataFrame
        очищена фінальна таблиця, форму якої слід змінити та зберегти
    name : str
        ПІБ декларанта, яке використовується як назва файлу
    excel : bool, default 'False'
        Записує дані такого вмісту '2018| https://public.na...' в .csv файл
        Якщо True, змінить таблицю та запише як .xlsx файл
    """

    if excel:
        df["paste"] = df["declaration_year"].astype(str).str.cat(df["link"], sep="| ")
        df = df[["paste", "gift_num", "property_num", "vehicle_num"]]
        df.columns = ["Скопіювати", "Подарунок", "Нерухоме", "Рухоме"]
        df.to_excel(f"./декларації/{name}.xlsx", index=False)
    else:
        paste = df["declaration_year"].astype(str).str.cat(df["link"], sep="| ")
        pd.DataFrame(paste).to_csv(f"./декларації/{name}.csv", index=False)


if __name__ == "__main__":

    os.makedirs("./декларації/", exist_ok=True)

    with open("names.txt", encoding="utf-8") as file:
        names_list = file.read().splitlines()

    for person in names_list:
        person = person.strip().partition(".")[0]
        try:
            url = f"http://declarations.com.ua/search?q={person}+AND+суддя&deepsearch=on&format=opendata"
            r = requests.get(url, sleep(0.5)).json()

            table = create_dataframe(r["results"]["object_list"], detailed=True)
            reshaped_df = reshape_dataframe(table, person)
            frame = rm_datedups(reshaped_df)

            if frame.empty:
                raise ValueError
            else:
                save(frame, person, excel=True)

        except ValueError:
            with open("./декларації/не_отримані.txt", "a") as ve:
                ve.write(f"{person}\n")
