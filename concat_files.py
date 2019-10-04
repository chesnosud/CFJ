import os, datetime
import pandas as pd


def concat_files(folder: str) -> None:
    """    
    Об'єднує усі файли з розширенням .xlsx в межах однієї папки
    
    Parameters
    ----------
    folder : str
        Папка із файлами, `folder="звільнення"`
    """

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder)
    files = [pd.read_excel(os.path.join(path, f)) for f in os.listdir(path) if f.endswith(".xlsx")]

    df = pd.concat(files, ignore_index=True).drop_duplicates()
    name = f"combined_asof_{str(datetime.datetime.now().date())}.xlsx"
    df.to_excel(os.path.join(path, name), index=False)


if __name__ == "__main__":
    concat_files(folder="результати_кваліфоцінювання")
