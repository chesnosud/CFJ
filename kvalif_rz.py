import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from time import sleep


URL = ""
M = [
    "чоловік", "батько", "вітчим", "син", "брат", "дядько",
    "племінник", "небіж"
]
F = [
    "дружина", "мати", "матір", "мачуха", "донька", "дочка", "сестра",
    "тітка", "племінниця", "небога"
]


def get_relatives(name: str) -> pd.DataFrame:
    """ Отримує род. зв. у табличному форматі. """

    pib = "-".join(name.split(" ")).lower()
    
    response = requests.get(URL + pib)
    soup = BeautifulSoup(response.content, "html.parser")
    
    df = pd.read_html(soup.prettify())[0]
    df.columns = ["ПІБ", "Місце роботи", "Початок роботи", "Кінець роботи"]
    
    df["Посада"] = df["Місце роботи"].str.split("  ").str[1]
    df["Місце роботи"] = df["Місце роботи"].str.split("  ").str[0]
    df["Стать"] = df["ПІБ"].str.lower()
    df["Стать"] = np.select(
        condlist=[
            df["Стать"].str.contains("|".join(M)),
            df["Стать"].str.contains("|".join(F))
        ],
        choicelist=[
            "ЧОЛОВІК", "ЖІНКА"
        ],
        default="НЕВІДОМО"
    )

    return df.groupby("ПІБ").agg(list).to_dict("index")


def table_to_text(relatives: dict) -> iter:
    """ Конвертує род. зв. з табличного формату в текстовий """
        
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
        
        positions = [pairs[i][-1] for i in range(size-1)]
        places = [pairs[i][0] for i in range(size-1)]

        period_tuple = [(pairs[i][1], pairs[i][2])for i in range(size-1)]
        period = ['-'.join(pair) for pair in period_tuple]
        
        history = [f"{pos} ({prd}) в {plc}" for pos, prd, plc in zip(positions, period, places)]
        
        gender = relatives[name]["Стать"][0]
        word = "працювала" if gender=="ЖІНКА" else "працював"
        
        p1 = f"{name} - з {pairs[-1][1]} по {pairs[-1][2]} працює {pairs[-1][-1]} в {pairs[-1][0]}."
        p2 = f"До цього, протягом {pairs[0][1]}-{pairs[-1][1]}, {word} на таких посадах: {', '.join(history)} "
        
        if size > 1:
            yield " ".join([p1, p2])
        else:
            yield p1
            
            
def main():
    with open("relatives_input.txt", encoding="utf-8") as input_file:
        for name in input_file:
            relatives_dict = get_relatives(name)
            result = list(table_to_text(relatives_dict))
            with open("./relatives_output.txt", "a") as output_file:
                output_file.write(f"\n{name}:\n")
                for counter, value in enumerate(result, 1):
                    s = f"{counter}. {value}"
                    output_file.write(f"{s}\n")
            
            sleep(1)
            

if __name__ == "__main__":
    main()
