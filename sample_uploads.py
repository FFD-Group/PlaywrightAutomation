import pandas as pd
import os

SPREADSHEET_EXTENSIONS = [".csv", ".xls", ".xlsx"]


def get_file_column_names(filepath: str, skiprows: int) -> list[str]:

    if not os.path.isfile(filepath):
        raise ValueError("Filepath given doesn't exist: %s", filepath)

    extension = os.path.splitext(filepath)[1]
    if extension not in SPREADSHEET_EXTENSIONS:
        raise ValueError("File given is not a suitable format: %s", extension)

    if extension == SPREADSHEET_EXTENSIONS[0]:
        df = pd.read_csv(filepath, skiprows=skiprows)

        return list(df.columns)
