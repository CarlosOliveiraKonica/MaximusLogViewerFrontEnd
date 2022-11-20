"""File useful to interact with Excel spreadsheets."""

import pandas as pd


class ExcelReader:
    def __init__(self, sheet_name: str) -> None:
        self._xlsx_file = ""
        self._sheet_name = sheet_name
        self._dataframe = pd.DataFrame()

    def set_file(self, xlsx_file: str) -> None:
        self._xlsx_file = xlsx_file
        self._dataframe = pd.read_excel(
            self._xlsx_file,
            sheet_name=self._sheet_name
        )

    def get_dataframe(self) -> pd.DataFrame:
        return self._dataframe.copy()

    def get_sheet_name(self) -> str:
        return self._sheet_name
