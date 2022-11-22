"""File useful to display special pages related to Log Statistics."""

from abc import ABC

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from common.tables import StatisticsTableInterface, LogLegendTable


class StatisticsPageInterface(ABC):
    """Abstract class useful to show statistics related to parameters such as mA, kV, Warning, etc."""
    
    def __init__(self, statistics_table: StatisticsTableInterface, log_table: LogLegendTable) -> None:
        self._statistics_table = statistics_table
        self._log_table = log_table

        # Log filter
        self._selected_logs_names = []
        self._selected_logs_indexes = []
        self._columns_selected_per_logs = []

        # Key column filter
        self._key_column = self._statistics_table.get_key_column()
        self._rows_selected_from_column_dict = {}

        # Dataframes
        self._filtered_dataframe = pd.DataFrame()
        self._total_dataframe = pd.DataFrame()

        self._selector_key = 0


    def show_page_header(self) -> None:
        st.header("Estatísticas de " + self._statistics_table.get_sheet_name())


    def __next_selector_key(self):
        """Workaround to solve DuplicatedWidgetID exception from Streamlit.
        This will generate unique IDs for selection widgets based on 'sheet_name'.
        """
        self._selector_key += 1
        return self._statistics_table.get_sheet_name() + str(self._selector_key)


    def show_log_filter(self) -> None:
        log_selection = st.multiselect('\nLogs sob análise:', self._log_table.get_logs_names(), key=self.__next_selector_key())
        if log_selection:
            self._selected_logs_names = log_selection
        else:
            self._selected_logs_names = self._log_table.get_logs_names()
        self._selected_logs_indexes = self._log_table.get_log_indexes_by_names(self._selected_logs_names)
        self._columns_selected_per_logs = self._statistics_table.get_all_columns_including_logs(self._selected_logs_indexes)


    def __get_column_name(self, column_name: str) -> str:
        if column_name is None:
            return self._key_column
        else:
            return column_name

    def __get_user_message_to_filter(self, column_name: str) -> str:
        return '\nFiltro de {}:'.format(column_name)

    def __get_rows_list_from_column(self, column_name: str) -> list:
        rows_list = self._statistics_table.get_rows_list_from_column(column_name, non_duplicated=True, non_nan=True)
        non_included_values_list = ["TOTAL", "", " "]
        for non_included_value in non_included_values_list:
            try:
                rows_list.remove(non_included_value)
            except ValueError:
                pass
        return rows_list


    def __add_total_row_to_rows_selected_dict(self, column_name: str, rows_selected: list) -> None:
        rows_selected.append("TOTAL")
        self._rows_selected_from_column_dict[column_name] = rows_selected


    def __initial_routine_for_column_filter(self, column_name: str) -> tuple:
        column_name = self.__get_column_name(column_name)
        user_message = self.__get_user_message_to_filter(column_name)
        rows_list = self.__get_rows_list_from_column(column_name)
        return column_name, user_message, rows_list
            
    def __final_routine_for_column_filter(self, column_name: str, rows_selected_from_column: list) -> None:
        self.__add_total_row_to_rows_selected_dict(column_name, rows_selected_from_column)


    def show_valid_values_checkbox(self):
        return st.checkbox("Filtrar somente valores válidos", value=True, key=self.__next_selector_key())


    def show_column_multi_select_filter(
        self, column_name=None, valid_selection_list=[], show_valid_checkbox=None, forced_checkbox_value=None
        ) -> None:
        """Show a multi selection filter, given the 'valid_selection_list'.
        
        If 'column_name' is omitted, then uses the 'key_column'.
        If 'valid_selection_list' is ommited, then the 'valid values filter' is also omitted.
        """
        column_name, user_message, rows_list = self.__initial_routine_for_column_filter(column_name)
        valid_checkbox_option = None
        if show_valid_checkbox:
            valid_checkbox_option = self.show_valid_values_checkbox()
        if valid_checkbox_option or forced_checkbox_value:
            rows_list = [row for row in rows_list if row in valid_selection_list]
        rows_selected_from_column = st.multiselect(user_message, rows_list, rows_list, key=self.__next_selector_key())
        self.__final_routine_for_column_filter(column_name, rows_selected_from_column)

    def show_column_range_select_filter(
        self, column_name=None, valid_range_min=None, valid_range_max=None, show_valid_checkbox=None, forced_checkbox_value=None
        ) -> None:
        """Show a range selection filter, given the 'valid_range_min' and 'valid_range_max'.
        
        If 'column_name' is omitted, then uses the 'key_column'.
        If 'valid_range_min' or 'valid_range_max' are ommited, then the 'valid values filter' is also omitted.
        """
        column_name, user_message, rows_list = self.__initial_routine_for_column_filter(column_name)
        valid_checkbox_option = None
        if show_valid_checkbox:
            valid_checkbox_option = self.show_valid_values_checkbox()
        if valid_checkbox_option or forced_checkbox_value:
            rows_list = [row for row in rows_list if (isinstance(row, int)) or (isinstance(row, float))]
            rows_list = [row for row in rows_list if (row >= valid_range_min) and (row <= valid_range_max)]
        min_value = int(min(rows_list))
        max_value = int(max(rows_list))
        range_value = list(range(min_value, max_value+1))
        min_value, max_value = st.select_slider(user_message, options=range_value, value=(min_value, max_value), key=self.__next_selector_key())
        rows_selected_from_column = [value for value in rows_list if value >= min_value and value <= max_value]
        self.__final_routine_for_column_filter(column_name, rows_selected_from_column)


    def __remove_total_column(self) -> pd.DataFrame:
        return self._total_dataframe.drop("TOTAL", axis="columns", errors="ignore")

    def __add_total_column(self) -> pd.DataFrame:
        logs_dataframe = self._total_dataframe[self._selected_logs_indexes]
        self._total_dataframe.loc[:,["TOTAL"]] = logs_dataframe.sum(numeric_only=True, axis=1)
        return self._total_dataframe

    def __remove_total_line(self) -> pd.DataFrame:
        self._total_dataframe = self._total_dataframe.drop(self._total_dataframe[self._total_dataframe[self._key_column] == "TOTAL"].index)
        return self._total_dataframe

    def __add_total_line(self) -> pd.DataFrame:
        total_line_dataframe = self.__get_total_line_dataframe()
        self._total_dataframe = pd.concat([self._total_dataframe, total_line_dataframe], ignore_index=True)
        self._total_dataframe.fillna(pd.NA, inplace=True)
        return self._total_dataframe


    def __get_total_line_dataframe(self) -> pd.DataFrame:
        columns_list = self._selected_logs_indexes
        columns_list.append(self._statistics_table.get_total_column())
        data_list = [[self._total_dataframe[column].sum()] for column in columns_list]
        columns_list.insert(0, self._key_column)
        data_list.insert(0, pd.NA)
        return pd.DataFrame(dict(zip(columns_list, data_list)))



    def __get_dataframe_filtered_by_rows_and_columns(
        self, 
        dataframe: pd.DataFrame, 
        col_to_select_rows: str, 
        rows_list: list, 
    ) -> pd.DataFrame:
        if rows_list:
            return dataframe[dataframe[col_to_select_rows].isin(rows_list)]
        else:
            return dataframe


    def show_log_and_statistics_table(self) -> None:
        left_col_width = 3
        right_col_width = 7
        left_col, right_col = st.columns([left_col_width, right_col_width])
        with left_col:
            st.write("\nLegenda de logs")
            log_dataframe = self._log_table.get_dataframe()
            log_dataframe = self._log_table.get_dataframe_filtered_by_logs_indexes(self._selected_logs_indexes)
            st.write(log_dataframe.astype(str))
        with right_col:
            st.write("\nTabela de quantidade por {}".format(self._statistics_table.get_sheet_name()))
            filtered_dataframe = self._statistics_table.get_dataframe_filtered_by_columns(self._columns_selected_per_logs)
            for column, rows_selected in self._rows_selected_from_column_dict.items():
                filtered_dataframe = self.__get_dataframe_filtered_by_rows_and_columns(
                    filtered_dataframe,
                    col_to_select_rows=column,
                    rows_list=rows_selected,
                )
            self._total_dataframe = filtered_dataframe.copy()
            self._total_dataframe = self.__remove_total_column()
            self._total_dataframe = self.__add_total_column()
            self._total_dataframe = self.__remove_total_line()
            self._total_dataframe = self.__add_total_line()
            st.dataframe(self._total_dataframe)


    def show_bar_chart(self) -> None:
        st.write("\nGráfico de barras: quantidade por {}".format(self._statistics_table.get_sheet_name()))
        chart_dataframe = self._total_dataframe.copy()
        chart_dataframe = chart_dataframe.dropna()
        chart_dataframe = chart_dataframe.rename(columns={self._key_column: 'index'})
        chart_dataframe = chart_dataframe.drop("TOTAL", axis="columns", errors="ignore")
        chart_dataframe = chart_dataframe.drop(self._statistics_table.get_sub_key_columns(), axis="columns", errors="ignore")
        chart_dataframe = chart_dataframe.set_index('index')
        st.bar_chart(chart_dataframe)

    def show_pie_chart(self) -> None:
        # Log sub-selection
        selection_with_total = self._selected_logs_names.copy()
        selection_with_total.append("TOTAL")
        selection = st.selectbox('\nGráfico de pizza: selecione a fonte de dados:', selection_with_total, key=self.__next_selector_key())
        if selection != "TOTAL":
            log_selected = self._log_table.get_log_index_by_name(selection)
        else:
            log_selected = selection

        # Chart
        chart_dataframe = self._total_dataframe.copy()
        chart_dataframe = chart_dataframe.dropna()
        chart_dataframe = chart_dataframe.drop(chart_dataframe[chart_dataframe[self._key_column] == "TOTAL"].index)
        figure = go.Figure(
            go.Pie(
                labels = chart_dataframe[self._key_column].to_list(),
                values = chart_dataframe[log_selected].to_list(),
                automargin = False
            )
        )
        st.plotly_chart(figure, use_container_width=True)


class mA_StatisticsPage(StatisticsPageInterface):
    
    MA_VALID_SELECTION_LIST = [10, 50, 100, 125, 160, 220, 280, 320, 360, 400, 450, 500, 630, 800]
    
    def __init__(self, statistics_table: StatisticsTableInterface, log_table: LogLegendTable) -> None:
        super().__init__(statistics_table, log_table)

    def show_page(self) -> None:
        self.show_page_header()
        self.show_log_filter()
        self.show_column_multi_select_filter(
            valid_selection_list=mA_StatisticsPage.MA_VALID_SELECTION_LIST,
            show_valid_checkbox=True,
        )
        self.show_log_and_statistics_table()
        self.show_bar_chart()
        self.show_pie_chart()


class kV_StatisticsPage(StatisticsPageInterface):

    KV_VALID_RANGE_MIN = 40
    KV_VALID_RANGE_MAX = 150

    def __init__(self, statistics_table: StatisticsTableInterface, log_table: LogLegendTable) -> None:
        super().__init__(statistics_table, log_table)

    def show_page(self) -> None:
        self.show_page_header()
        self.show_log_filter()
        self.show_column_range_select_filter(
            valid_range_min=kV_StatisticsPage.KV_VALID_RANGE_MIN,
            valid_range_max=kV_StatisticsPage.KV_VALID_RANGE_MAX,
            show_valid_checkbox=True,
        )
        self.show_log_and_statistics_table()
        self.show_bar_chart()
        self.show_pie_chart()


class ms_StatisticsPage(StatisticsPageInterface):

    MS_VALID_RANGE_MIN = 1
    MS_VALID_RANGE_MAX = 5000

    def __init__(self, statistics_table: StatisticsTableInterface, log_table: LogLegendTable) -> None:
        super().__init__(statistics_table, log_table)

    def show_page(self) -> None:
        self.show_page_header()
        self.show_log_filter()
        self.show_column_range_select_filter(
            valid_range_min=ms_StatisticsPage.MS_VALID_RANGE_MIN,
            valid_range_max=ms_StatisticsPage.MS_VALID_RANGE_MAX,
            show_valid_checkbox=True,
        )
        self.show_log_and_statistics_table()
        self.show_bar_chart()
        self.show_pie_chart()


class Failure_StatisticsPage(StatisticsPageInterface):

    def __init__(self, statistics_table: StatisticsTableInterface, log_table: LogLegendTable) -> None:
        super().__init__(statistics_table, log_table)

    def show_page(self) -> None:
        self.show_page_header()
        self.show_log_filter()
        self.show_column_multi_select_filter()
        self.show_log_and_statistics_table()
        self.show_bar_chart()
        self.show_pie_chart()


class Warning_StatisticsPage(StatisticsPageInterface):

    def __init__(self, statistics_table: StatisticsTableInterface, log_table: LogLegendTable) -> None:
        super().__init__(statistics_table, log_table)

    def show_page(self) -> None:
        self.show_page_header()
        self.show_log_filter()
        self.show_column_multi_select_filter()
        self.show_log_and_statistics_table()
        self.show_bar_chart()
        self.show_pie_chart()


class Exposition_StatisticsPage(StatisticsPageInterface):

    def __init__(self, statistics_table: StatisticsTableInterface, log_table: LogLegendTable) -> None:
        super().__init__(statistics_table, log_table)

    def show_page(self) -> None:
        self.show_page_header()
        self.show_log_filter()
        valid_values_checkbox_option = self.show_valid_values_checkbox()
        self.show_column_multi_select_filter(
            column_name="mA",
            valid_selection_list=mA_StatisticsPage.MA_VALID_SELECTION_LIST,
            forced_checkbox_value=valid_values_checkbox_option,
        )
        self.show_column_range_select_filter(
            column_name="kV",
            valid_range_min=kV_StatisticsPage.KV_VALID_RANGE_MIN,
            valid_range_max=kV_StatisticsPage.KV_VALID_RANGE_MAX,
            forced_checkbox_value=valid_values_checkbox_option,
        )
        self.show_column_range_select_filter(
            column_name="ms",
            valid_range_min=ms_StatisticsPage.MS_VALID_RANGE_MIN,
            valid_range_max=ms_StatisticsPage.MS_VALID_RANGE_MAX,
            forced_checkbox_value=valid_values_checkbox_option,
        )
        self.show_column_range_select_filter(column_name="mAs")
        self.show_column_range_select_filter(column_name="kW")
        self.show_column_range_select_filter(column_name="kJ")
        self.show_column_multi_select_filter(column_name="Ganho mA")
        self.show_column_multi_select_filter(column_name="Indutor")
        self.show_log_and_statistics_table()
