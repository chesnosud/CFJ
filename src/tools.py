import pandas as pd
from pathlib import Path
from datetime import datetime


def concat_files(path: Path, ext: str) -> None:
    """    
    Об'єднує усі файли з розширенням .xlsx в межах однієї папки
    
    Parameters
    ----------
    folder : str
        Папка із файлами, `folder="звільнення"`
    """

    files = [pd.read_excel(path / f) for f in path.rglob(ext)]
    df = pd.concat(files, ignore_index=True).drop_duplicates()
    
    keyword, suffix = ext.strip("*").split(".")
    name = f"{str(datetime.now().date())}_{keyword}_combined.{suffix}"
    df.to_excel(path / name, index=False) if suffix == "xlsx" else df.to_csv(path / name, index=False)