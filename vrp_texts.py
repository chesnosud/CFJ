import re
import requests
from bs4 import BeautifulSoup
from nltk import sent_tokenize
from typing import Iterable, List


def raw_text(url: str) -> str:
    """ Отримує текст рішення з сайту ВРП"""

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    text_container = []
    for p in soup.select(
        "div.field.field-name-field-body.field-type-text-long.field-label-hidden > div > div"
    ):
        text_container.append(p.text)

    return " ".join(text_container)


# def text_generator(soup: bs4.BeautifulSoup) -> Iterable[str]:
#     """ Як альтерантива функції вище, але з генератором

#     >>> s = " ".join(list(text_generator(soup)))
#     """
#     for p in soup.select(
#         "div.field.field-name-field-body.field-type-text-long.field-label-hidden > div > div"
#     ):
#         yield p.text


def clean_text(s: str, spam: List[str, str] = ["\xa0", "\n"]) -> str:
    """ Прибирає з тексту зайві символи"""

    s1 = re.sub(pattern="|".join(spam), repl=" ", string=s).strip()
    return re.sub(pattern="\s+", repl=" ", string=s1)


def vzhyttia_zahodiv(s: str, num_sent: int) -> None:
    """ Виводить заповнений шаблонний текст по матеріалах 
    щодо вжиття заходів щодо забезпечення незалежності суддів 
    
    ---
    змінні: 
           s: Текст рішення
        date: Дата звернення 
        name: ПІБ судді
        desc: Опис суті
    num_sent: Кількість речень після збігу в суті
    decision: Висновок ВРП
    
    ---
    TO-DO:
    замість enumerate і умовної кількості речень після збігу,
    знайти закономірності і написати регулярний вираз для desc;
    """

    # Дата та ПІБ
    date = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", s).group(1)
    name = re.search(r"\bСуддя\b\s+(\w+\s\w\.\w\.)", s).group(1)

    # Опис суті, додає num_sent після збігу по ключову слову
    sentences_list = sent_tokenize(s)
    my_answers = []
    for index, sentence in enumerate(sentences_list):
        if "у повідомленні" in sentence:
            my_answers.append(sentences_list[index : index + num_sent])

    desc = "\n".join([item for sublist in my_answers for item in sublist])

    # Висновок ВРП
    decision = s.split("вирішила:")[-1].split(".")[0].strip()

    # Шаблон
    text_template = f"""
    [ВСТУП]
    Відповідно до рішення Вищої ради правосуддя, {date} суддя {name} зверну-вся/-лась з повідомленням про втручання у його/її діяльність як судді.
    [ОПИС]
    {desc}
    [Висновок]
    У зв’язку із зазначеним, Вища рада правосуддя вирішила {decision}."""

    def output(s: str) -> None:
        """ Виводить розділений за рядками текст"""

        for part in s.split("\n"):
            print(part)

    return output(text_template)


if __name__ == "__main__":
    s = raw_text("http://hcj.gov.ua/doc/doc/1")
    s1 = clean_text(s)
    vzhyttia_zahodiv(s1, 5)