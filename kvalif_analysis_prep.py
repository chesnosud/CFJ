import sys

import numpy as np
import pandas as pd


def get_data(filename="./data/kalendar.xlsx"):
    try:
        df = pd.read_excel(filename)
    except FileNotFoundError:
        sys.exit("Файлу не знайдено")

    df["Результат оцінювання"] = df["Результат оцінювання"].str.strip()
    df["Рішення (посилання)"] = df["Рішення (посилання)"].str.strip()
    #     df = df.drop_duplicates(['Рішення (посилання)', 'Область'], keep='last')
    df["Результат оцінювання"] = df["Результат оцінювання"].str.strip()
    df["Дата кваліфоцінювання"] = df["Дата кваліфоцінювання"].astype("datetime64[s]")
    df["Дата кваліфоцінювання"] = df["Дата кваліфоцінювання"].dt.floor("d")
    df["Порушення доброчесності"] = df["Порушення доброчесності"].fillna(0)
    df["Чи є профайл"] = df["Чи є профайл"].fillna(0)
    return df


def cleaning_results(df):
    df["Результат оцінювання"] = np.select(
        condlist=[
            df["Результат оцінювання"].str.contains("зупинено", na=False),
            df["Результат оцінювання"].str.contains("припинено", na=False),
            df["Результат оцінювання"].str.contains("перерв", na=False),
            df["Результат оцінювання"].str.contains("відкладен", na=False),
            df["Результат оцінювання"].str.contains("не відповідає", na=False),
            df["Результат оцінювання"].str.contains(
                "відповідає займаній посаді|відповідає|подання про звільнення|призначення|переведення|рекомендовано",
                na=False,
            ),
            df["Результат оцінювання"].str.contains("знято", na=False),
            df["Результат оцінювання"].str.contains("http", na=False),
            df["Результат оцінювання"].str.contains("не з'явився", na=False),
            df["Результат оцінювання"].str.contains("відкладено", na=False),
            df["Результат оцінювання"].str.contains("відсторонений", na=False),
            df["Результат оцінювання"].str.contains("відмова", na=False),
        ],
        choicelist=[
            "Зупинено",
            "Припинено",
            "Перерва",
            "Відкладено",
            "Не відповідає",
            "Відповідає",
            "Знято",
            "Звільнений",
            "Не з'явився",
            "Відкладено",
            "Тимчасово відсторонений",
            "Відмова від проходження",
        ],
        default="Категорія відсутня",
    )
    return df


def cleaning_oblast(df):
    df["Область"] = np.select(
        condlist=[
            df["Область"].str.contains("Київськ", na=False, case=False),
            df["Область"].str.contains("ки[їє]в", na=False, case=False),
            df["Область"].str.contains("харк", na=False, case=False),
            df["Область"].str.contains("львів", na=False, case=False),
            df["Область"].str.contains("дніпро", na=False, case=False),
            df["Область"].str.contains("закарп", na=False, case=False),
            df["Область"].str.contains("Хмельн", na=False, case=False),
            df["Область"].str.contains("одес", na=False, case=False),
            df["Область"].str.contains("полтав", na=False, case=False),
            df["Область"].str.contains("Житомир", na=False, case=False),
            df["Область"].str.contains("Волин", na=False, case=False),
            df["Область"].str.contains("рівн", na=False, case=False),
            df["Область"].str.contains("донець", na=False, case=False),
            df["Область"].str.contains("микола", na=False, case=False),
            df["Область"].str.contains("Черкас", na=False, case=False),
            df["Область"].str.contains("кіровог", na=False, case=False),
            df["Область"].str.contains("запорі", na=False, case=False),
            df["Область"].str.contains("вінни", na=False, case=False),
            df["Область"].str.contains("луган", na=False, case=False),
            df["Область"].str.contains("терноп", na=False, case=False),
            df["Область"].str.contains("черніг", na=False, case=False),
            df["Область"].str.contains("чернів", na=False, case=False),
            df["Область"].str.contains("івано", na=False, case=False),
            df["Область"].str.contains("херсон", na=False, case=False),
            df["Область"].str.contains("сум", na=False, case=False),
            df["Область"].str.contains("крим", na=False, case=False),
        ],
        choicelist=[
            "Київcька область",
            "м. Київ",
            "Харківська область",
            "Львівська область",
            "Дніпропетровська область",
            "Закарпатська область",
            "Хмельницька область",
            "Одеська область",
            "Полтавська область",
            "Житомирська область",
            "Волинська область",
            "Рівненська область",
            "Донецька область",
            "Миколаївська область",
            "Черкаська область",
            "Кіровоградська область",
            "Запорізька область",
            "Вінницька область",
            "Луганська область",
            "Тернопільська область",
            "Чернігівська область",
            "Чернівецька область",
            "Івано-Франківська область",
            "Херсонська область",
            "Сумська область",
            "АР Крим",
        ],
        default="Категорія відсутня",
    )
    return df


def count_q(df):
    counts = df["Результат оцінювання"].value_counts().reset_index()
    counts.columns = ["Статус", "Кількість"]
    # counts = counts.loc[counts['Статус'].ne('Тимчасово відсторонений')]
    counts["perc"] = (counts["Кількість"].astype(int) / len(df)) * 100
    counts["perc"] = counts["perc"].round(2).astype(str) + "%"
    counts.columns = ["Статус", "К-сть", "К-сть, %"]

    kks_nd = []
    for c in counts["Статус"]:
        kks_nd.append(df.loc \
            [df["Порушення доброчесності"].eq(1)& df["Результат оцінювання"].eq(c)]
        )

    counts['К-сть недоброчесних'] = kks_nd

    counts["К-сть недоброчесних, % від категорії"] = (
        counts["К-сть недоброчесних"].astype(int) / counts["К-сть"].astype(int)
    ) * 100

    counts["К-сть недоброчесних, % усіх"] = (
        counts["К-сть недоброчесних"].astype(int) / len(df)
    ) * 100

    counts["К-сть недоброчесних, % від категорії"] = (
        counts["К-сть недоброчесних, % від категорії"].round(2).astype(str) + "%"
    )

    counts["К-сть недоброчесних, % усіх"] = (
        counts["К-сть недоброчесних, % усіх"].round(2).astype(str) + "%"
    )

    counts = counts.append(counts.sum(numeric_only=True), ignore_index=True)
    counts.iloc[-1, 0] = "Загалом"
    counts.iloc[-1, 2] = "100%"
    counts["К-сть"] = counts["К-сть"].astype(int)
    counts["К-сть недоброчесних"] = counts["К-сть недоброчесних"].astype(int)
    return counts


def group_data(df):
    g = (
        df.groupby(["Область", "Результат оцінювання", "Порушення доброчесності"])
        .size()
        .unstack(fill_value=0)
    )
    grouped = g.reset_index()
    grouped.columns = [
        "Область", "Результат оцінювання", "Доброчесний", "Недоброчесний",
    ]
    grouped["Загалом"] = (
        grouped["Доброчесний"].astype(int) + grouped["Недоброчесний"].astype(int)
    )

    return grouped


def recategorize(df):
    new_categories = {
        "Відповідає": ["Відповідає"],
        "Не відповідає": ["Не відповідає"],
        "Інше": [
            "Звільнений", "Знято", "Перерва", "Відкладено","Зупинено", 
            "Не з'явився", "Відмова від проходження", "Припинено",
        ]
    }
    categories = {v: k for k, vv in new_categories.items() for v in vv}
    new_df = df.copy()
    new_df["Результат оцінювання"] = new_df["Результат оцінювання"].map(categories)
    return new_df
