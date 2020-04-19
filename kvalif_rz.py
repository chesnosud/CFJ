import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep


URL = ""
M = ["чоловік", "батько", "вітчим", "син", "брат", "дядько", "племінник", "небіж"]
F = [
    "дружина",
    "мати",
    "матір",
    "мачуха",
    "донька",
    "дочка",
    "сестра",
    "тітка",
    "племінниця",
    "небога",
]


def load_page(url: str):
    """ Повертає вміст сторінки через selenium. """

    options = Options()
    options.headless = True

    with webdriver.Chrome("./chromedriver.exe", options=options) as browser:
        browser.get(url)
        sleep(np.random.uniform(2, 7))
        html = browser.page_source
    return html


def get_relatives(name: str) -> dict:
    """ Отримує род. зв. у табличному форматі. """

    dashed_name = "-".join(name.split(" ")).lower()

    html = load_page(URL + dashed_name)
    soup = BeautifulSoup(html, "html.parser")

    df = pd.read_html(soup.prettify())[0]
    df.columns = ["ПІБ", "Місце роботи", "Початок роботи", "Кінець роботи"]

    # split на подвійному пробілі
    df["Посада"] = df["Місце роботи"].str.split("  ").str[1]
    df["Місце роботи"] = df["Місце роботи"].str.split("  ").str[0]
    df["Стать"] = df["ПІБ"].str.lower()
    df["Стать"] = np.select(
        condlist=[
            df["Стать"].str.contains("|".join(M)),
            df["Стать"].str.contains("|".join(F)),
        ],
        choicelist=["ЧОЛОВІК", "ЖІНКА"],
        default="НЕВІДОМО",
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
            relatives[name].get("Посада", ""),
        ):
            pairs.append(pair)

        gender = relatives[name]["Стать"][0]
        word = "працювала" if gender == "ЖІНКА" else "працював"

        size = len(pairs)

        positions = [pairs[i][-1] for i in range(size - 1)]
        places = [pairs[i][0] for i in range(size - 1)]

        tenure_tuple = [(pairs[i][1], pairs[i][2]) for i in range(size - 1)]
        tenure = ["-".join(pair) for pair in tenure_tuple]

        past_experience = [
            f"{pos} ({prd}) в {plc}" for pos, prd, plc in zip(positions, tenure, places)
        ]
        exp = ", ".join(past_experience)

        p1 = f"{name} - з {pairs[-1][1]} по {pairs[-1][2]} працює {pairs[-1][-1]} в {pairs[-1][0]}."
        p2 = f"До цього, протягом {pairs[0][1]}-{pairs[-1][1]}, {word} на таких посадах: {exp}."

        if size > 1:
            yield " ".join([p1, p2])
        else:
            yield p1


def main():
    with open("relatives_input.txt", encoding="utf-8") as input_file:
        for name in input_file:
            relatives_dict = get_relatives(name)
    
            try:
                result = list(table_to_text(relatives_dict))
            except TypeError:
                result = "Сталася помилка"

            with open("./relatives_output.txt", "a") as output_file:
                output_file.write(f"\n{name}:\n")
                if isinstance(result, str):
                    output_file.write("Сталася помилка\n")
                else:
                    for counter, value in enumerate(result, 1):
                        s = f"{counter}. {value}"
                        output_file.write(f"{s}\n")


if __name__ == "__main__":
    main()
