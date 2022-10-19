import pandas as pd

from common.excel_reader import ExcelReader


class TableInterface:
    def __init__(self, sheet_name: str) -> None:
        self._excel_reader = ExcelReader(sheet_name)

    def set_file(self, xlsx_file: str) -> None:
        self._excel_reader.set_file(xlsx_file)

    def get_dataframe(self) -> pd.DataFrame:
        return self._excel_reader.get_dataframe()

    def get_sheet_name(self) -> str:
        return self._excel_reader.get_sheet_name()


class LogLegendTable(TableInterface):

    COLUMN_INDEXES = "Índice"
    COLUMN_FILES = "Arquivo"

    def __init__(self) -> None:
        super().__init__("Legenda")
        self._logs_dict = {}
        self._logs_indexes = []
        self._logs_names = []

    def __get_logs_dict(self) -> dict:
        logs_dataframe = self._excel_reader.get_dataframe()
        logs_dataframe_indexes = logs_dataframe[LogLegendTable.COLUMN_INDEXES].to_list()
        logs_dataframe_files = logs_dataframe[LogLegendTable.COLUMN_FILES].to_list()
        return dict(zip(logs_dataframe_indexes, logs_dataframe_files))

    def __get_logs_indexes(self) -> list:
        return list(self._logs_dict.keys())

    def __get_logs_names(self) -> list:
        return list(self._logs_dict.values())

    def set_file(self, xlsx_file: str) -> None:
        self._excel_reader.set_file(xlsx_file)
        self._logs_dict = self.__get_logs_dict()
        self._logs_indexes = self.__get_logs_indexes()
        self._logs_names = self.__get_logs_names()

    def get_dataframe(self) -> pd.DataFrame:
        dataframe = self._excel_reader.get_dataframe()
        return dataframe[[LogLegendTable.COLUMN_INDEXES, LogLegendTable.COLUMN_FILES]]

    def get_dataframe_filtered_by_logs_indexes(self, logs_indexes: list) -> pd.DataFrame:
        dataframe = self.get_dataframe()
        return dataframe[dataframe[LogLegendTable.COLUMN_INDEXES].isin(logs_indexes)]

    def get_logs_dict(self) -> dict:
        return self._logs_dict.copy()

    def get_logs_indexes(self) -> list:
        return self._logs_indexes.copy()

    def get_logs_names(self) -> list:
        return self._logs_names.copy()

    def get_log_name_by_index(self, index: int) -> str:
        return self._logs_dict.get(index, "")

    def get_log_names_by_indexes(self, index_list: list) -> list:
        return [self.get_log_name_by_index(log_index) for log_index in index_list]

    def get_log_index_by_name(self, name: str) -> int:
        index = self._logs_names.index(name)
        return self._logs_indexes[index]

    def get_log_indexes_by_names(self, name_list: list) -> list:
        return [self.get_log_index_by_name(log_name) for log_name in name_list]


class StatisticsTableInterface(TableInterface):
    def __init__(self, sheet_name: str, key_column: str, sub_key_columns: list = []) -> None:
        super().__init__(sheet_name)
        self._key_column = key_column
        self._sub_key_columns = sub_key_columns
        self._total_column = "TOTAL"

        self._main_columns = []
        self._main_columns.extend([self._key_column])
        self._main_columns.extend(self._sub_key_columns)
        self._main_columns.extend([self._total_column])

    def get_key_column(self) -> str:
        return self._key_column

    def get_sub_key_columns(self) -> list:
        return self._sub_key_columns.copy()

    def get_total_column(self) -> str:
        return self._total_column

    def get_logs_columns(self) -> list:
        columns = list(self.get_dataframe())
        return [col for col in columns if col not in self._main_columns]

    def get_all_columns(self) -> list:
        return list(self.get_dataframe())

    def get_all_columns_including_logs(self, logs_columns: list) -> list:
        columns = [self.get_key_column()]
        columns.extend(self.get_sub_key_columns())
        columns.extend(logs_columns)
        columns.extend([self.get_total_column()])
        return columns

    def get_dataframe_filtered_by_columns(self, columns_list: list) -> pd.DataFrame:
        dataframe = self.get_dataframe()
        if columns_list:
            return dataframe[columns_list]
        else:
            return dataframe

    def get_dataframe_filtered_by_rows_and_column(self, rows_list: list, column: str) -> pd.DataFrame:
        dataframe = self.get_dataframe()
        if rows_list:
            return dataframe[dataframe[column].isin(rows_list)]
        else:
            return dataframe

    def get_dataframe_filtered_by_rows_and_columns(self, col_to_select_rows: str, rows_list: list, columns_list: list) -> pd.DataFrame:
        dataframe = self.get_dataframe_filtered_by_columns(columns_list)
        if rows_list:
            return dataframe[dataframe[col_to_select_rows].isin(rows_list)]
        else:
            return dataframe

    def get_rows_list_from_column(self, column: str, non_duplicated=False, non_nan=False) -> list:
        dataframe = self.get_dataframe()
        if non_nan:
            dataframe.dropna(inplace=True)
        rows_list = dataframe[column].to_list()
        if non_duplicated:
            rows_list = list(dict.fromkeys(rows_list))
            try:
                rows_list.sort()
            except TypeError:
                pass
        return rows_list


class mA_Table(StatisticsTableInterface):
    def __init__(self) -> None:
        super().__init__("mA", "mA")


class kV_Table(StatisticsTableInterface):
    def __init__(self) -> None:
        super().__init__("kV", "kV")


class ms_Table(StatisticsTableInterface):
    def __init__(self) -> None:
        super().__init__("ms", "ms")


class FailureTable(StatisticsTableInterface):
    def __init__(self) -> None:
        super().__init__("Falha", "Falha")


class WarningTable(StatisticsTableInterface):
    def __init__(self) -> None:
        super().__init__("Warning", "Warning")


class ExpositionTable(StatisticsTableInterface):
    def __init__(self) -> None:
        super().__init__("Exposição", "Exposição", ["mA", "kV", "ms"])


class StatisticsTables:
    def __init__(self) -> None:
        self.log_table = LogLegendTable()
        self.mA_table = mA_Table()
        self.kV_table = kV_Table()
        self.ms_table = ms_Table()
        self.failure_table = FailureTable()
        self.warning_table = WarningTable()
        self.exposition_table = ExpositionTable()

    def set_file(self, xlsx_file: str) -> None:
        self.log_table.set_file(xlsx_file)
        self.mA_table.set_file(xlsx_file)
        self.kV_table.set_file(xlsx_file)
        self.ms_table.set_file(xlsx_file)
        self.failure_table.set_file(xlsx_file)
        self.warning_table.set_file(xlsx_file)
        self.exposition_table.set_file(xlsx_file)
