import pandas as pd
import os

SPREADSHEET_EXTENSIONS = [".csv", ".xls", ".xlsx"]
MAX_COLUMN_VALUES = 10


def get_file_column_names(filepath: str, skiprows: int) -> list[str]:

    if not os.path.isfile(filepath):
        raise ValueError("Filepath given doesn't exist: %s", filepath)

    extension = os.path.splitext(filepath)[1]
    if extension not in SPREADSHEET_EXTENSIONS:
        raise ValueError("File given is not a suitable format: %s", extension)

    if extension == SPREADSHEET_EXTENSIONS[0]:
        df = pd.read_csv(filepath, skiprows=skiprows)
    else:
        df = pd.read_excel(filepath, skiprows=skiprows)

    return list(df.columns)


def get_column_values(
    filepath: str, skiprows: int, group_by_column: str
) -> list[str]:

    if not os.path.isfile(filepath):
        raise ValueError("Filepath given doesn't exist: %s", filepath)

    extension = os.path.splitext(filepath)[1]
    if extension not in SPREADSHEET_EXTENSIONS:
        raise ValueError("File given is not a suitable format: %s", extension)

    if extension == SPREADSHEET_EXTENSIONS[0]:
        df = pd.read_csv(filepath, skiprows=skiprows)
    else:
        df = pd.read_excel(filepath, skiprows=skiprows)

    return (
        df[group_by_column]
        .replace({float("nan"): None})
        .unique()[:MAX_COLUMN_VALUES]
    ).tolist()
