import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from Typing import Dict, List, Iterator


URL = ""


def rz(name: str) -> Dict[Dict[str, List[str]]]:
    """ Отримує род. зв. у табличному форматі. 

    name: ім'я у форматі: "Прізвище Ім'я По-батькові"
    ---

    >>> rz(name)
                             ПІБ               Місце роботи                     Посада Період роботи
    0  Іванов Іван Іванович       Оперативне управління ДПІ  cтарший оперуповноважений  2015—2016 рр.
    1  Іванов Іван Іванович       Оперативне управління ГУ   cтарший оперуповноважений  2016—2018 рр.
    2  Іванов НеІван Іванович     Державна Екологічна Інспе  головний спеціаліст відді  2012—2018 рр.
    3  НеІванов Неіван Неіваночи  Долинське відділення полі  поліцейський сектору реаг  2017—2017 рр.
    4  НеІванов Неіван Неіваночи  Долинське відділення полі  інспектор з ювенальної пр  2017—2018 рр.
    """

    pib = re.sub("\s+", "-", name).lower()
    response = requests.get(URL + pib)
    soup = BeautifulSoup(response.content, "html.parser")

    df = pd.read_html(soup.prettify())[0]
    df.columns = ["ПІБ", "Місце роботи", "Початок роботи", "Кінець роботи"]
    df["Посада"] = [em.text for em in soup.find_all("em")]

    return df.groupby("ПІБ").agg(list).to_dict("index")


def table_to_text(relatives: Dict[Dict[str, List[str]]]) -> Iterator[str]:
    """ Конвертує род. зв. з табличного формату в текстовий за форматом:
    ПІБ (ступінь спорідненості) -- з _остання дата початку роботу_ по 
    _остання дата закінчення роботи_ працює _остання посада_ в
    _останнє місце роботи_. До цього, протягом 
    _перша дата початку роботи_-_передостання дата останнього кінця роботи_,
    працював на таких посадах: _перелік у форматі "посада (період)".
    
    --------
    
    >>> s = list(table_to_text(df))
    """
    
    for name in relatives.keys():
        pairs = []
        for pair in zip(
            relatives[name].get("Місце роботи", ""),
            relatives[name].get("Початок роботи", ""),
            relatives[name].get("Кінець роботи", ""),
            relatives[name].get("Посада", "")
        ):
            pairs.append(pair)
        
        size = len(pairs)
        previous_positions_list = [pairs[i][-1] for i in range(size-1)]
        previous_positions_string = ', '.join(previous_positions_list) 
        previous_places = ', '.join([pairs[i][0] for i in range(size-1)])

        year_pairs_tuple = [(pairs[i][1], pairs[i][2])for i in range(size-1)]
        years = ['-'.join(pair) for pair in year_pairs_tuple]
        
        
        position_year = [f"{p} ({y})" for p,y in zip(previous_positions_list, years)]
        part1 = f"{name} - з {pairs[-1][1]} по {pairs[-1][2]} працює {pairs[-1][-1]} в {pairs[-1][0]}."
        part2 = f"До цього, протягом {pairs[0][1]}-{pairs[-1][1]}, працював на таких посадах: {', '.join(position_year)}"
        
        yield " ".join([part1, part2])


if __name__ == "__main__":
    name = "Іванов Іван Іванович"
    df = rz(name)
    s = list(table_to_text(df))
