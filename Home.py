import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from common.tables import StatisticsTableInterface, StatisticsTables, LogLegendTable


class StatisticsPage:
    def __init__(self, statistics_table: StatisticsTableInterface, log_table: LogLegendTable) -> None:
        self._statistics_table = statistics_table
        self._log_table = log_table

        # Log filter
        self._selected_logs_names = []
        self._selected_logs_indexes = []
        self._columns_selected_per_logs = []

        # Key column filter
        self._key_column = self._statistics_table.get_key_column()
        self._rows_selected_from_key_column = []

        # Dataframes
        self._filtered_dataframe = pd.DataFrame()
        self._total_dataframe = pd.DataFrame()


    def show_log_filter(self) -> None:
        log_selection = st.multiselect('\nLogs sob análise:', self._log_table.get_logs_names())
        if log_selection:
            self._selected_logs_names = log_selection
        else:
            self._selected_logs_names = self._log_table.get_logs_names()
        self._selected_logs_indexes = self._log_table.get_log_indexes_by_names(self._selected_logs_names)
        self._columns_selected_per_logs = self._statistics_table.get_all_columns_including_logs(self._selected_logs_indexes)


    def __get_key_column_message(self) -> str:
        return '\nFiltro de {}:'.format(self._statistics_table.get_sheet_name())

    def __get_rows_list_from_key_column(self) -> list:
        rows_list = self._statistics_table.get_rows_list_from_column(self._key_column)
        try:
            rows_list.remove("TOTAL")
        except ValueError:
            pass
        return rows_list

    def __add_total_row_to_rows_selected(self) -> None:
        self._rows_selected_from_key_column.append("TOTAL")

    def show_key_column_multi_select_filter(self) -> None:
        user_message = self.__get_key_column_message()
        rows_list = self.__get_rows_list_from_key_column()
        self._rows_selected_from_key_column = st.multiselect(user_message, rows_list, rows_list)
        self.__add_total_row_to_rows_selected()

    def show_key_column_range_select_filter(self) -> None:
        user_message = self.__get_key_column_message()
        rows_list = self.__get_rows_list_from_key_column()
        min_value, max_value = st.select_slider(user_message, options=rows_list, value=(min(rows_list), max(rows_list)))
        self._rows_selected_from_key_column = [value for value in rows_list if value >= min_value and value <= max_value]
        self.__add_total_row_to_rows_selected()


    def __remove_total_column(self) -> pd.DataFrame:
        return self._total_dataframe.drop("TOTAL", axis="columns", errors="ignore")

    def __get_total_line_dataframe(self) -> pd.DataFrame:
        columns_list = self._selected_logs_indexes
        columns_list.append(self._statistics_table.get_total_column())
        data_list = [[self._total_dataframe[column].sum()] for column in columns_list]
        columns_list.insert(0, self._key_column)
        data_list.insert(0, "TOTAL")
        return pd.DataFrame(dict(zip(columns_list, data_list)))

    def __add_total_line(self) -> pd.DataFrame:
        total_line_dataframe = self.__get_total_line_dataframe()
        self._total_dataframe = pd.concat([self._total_dataframe, total_line_dataframe], ignore_index=True)
        return self._total_dataframe

    def __remove_total_line(self) -> pd.DataFrame:
        self._total_dataframe = self._total_dataframe.drop(self._total_dataframe[self._total_dataframe[self._key_column] == "TOTAL"].index)
        return self._total_dataframe

    def __add_total_column(self) -> pd.DataFrame:
        self._total_dataframe.loc[:,["TOTAL"]] = self._total_dataframe.sum(numeric_only=True, axis=1)
        return self._total_dataframe

    def show_log_and_statistics_table(self) -> None:
        left_col_width = 1
        right_col_width = 3
        left_col, right_col = st.columns([left_col_width, right_col_width])
        with left_col:
            st.write("\nLegenda de logs")
            log_dataframe = self._log_table.get_dataframe()
            log_dataframe = log_dataframe.filter(items=self._selected_logs_indexes, axis="index")
            st.write(log_dataframe.astype(str))
        with right_col:
            st.write("\nTabela de quantidade por {}".format(self._statistics_table.get_sheet_name()))
            self._filtered_dataframe = self._statistics_table.get_dataframe_filtered_by_rows_and_columns(
                self._key_column, self._rows_selected_from_key_column, self._columns_selected_per_logs
            )
            self._total_dataframe = self._filtered_dataframe.copy()
            self._total_dataframe = self.__remove_total_column()
            self._total_dataframe = self.__add_total_column()
            self._total_dataframe = self.__remove_total_line()
            self._total_dataframe = self.__add_total_line()
            st.write(self._total_dataframe.astype(str))


    def show_bar_chart(self) -> None:
        st.write("\nGráfico de barras: quantidade por {}".format(self._statistics_table.get_sheet_name()))
        chart_dataframe = self._total_dataframe.copy()
        chart_dataframe = chart_dataframe.rename(columns={self._key_column: 'index'})
        chart_dataframe = chart_dataframe.drop("TOTAL", axis="columns", errors="ignore")
        chart_dataframe = chart_dataframe.drop(chart_dataframe[chart_dataframe['index'] == "TOTAL"].index)
        chart_dataframe = chart_dataframe.set_index('index')
        st.bar_chart(chart_dataframe)

    def show_pie_chart(self) -> None:
        # Log sub-selection
        selection_with_total = self._selected_logs_names.copy()
        selection_with_total.append("TOTAL")
        selection = st.selectbox('\nGráfico de pizza: selecione a fonte de dados:', selection_with_total)
        if selection != "TOTAL":
            log_selected = statistics.log_table.get_log_index_by_name(selection)
        else:
            log_selected = selection

        # Chart
        chart_dataframe = self._total_dataframe.copy()
        chart_dataframe = chart_dataframe.drop(chart_dataframe[chart_dataframe[self._key_column] == "TOTAL"].index)
        figure = go.Figure(
            go.Pie(
                labels = chart_dataframe[self._key_column].to_list(),
                values = chart_dataframe[log_selected].to_list(),
                automargin = False
            )
        )
        st.plotly_chart(figure, use_container_width=True)


statistics = StatisticsTables()

st.set_page_config(page_title="MaximusLogViewer", layout="wide")

st.write('# MaximusLogViewer')

uploaded_file = st.file_uploader('Selecione o arquivo EXCEL exportado pelo script do MaximusLogViewer:', type=[".xlsx"])

if uploaded_file:
    st.write(uploaded_file.name)
   
    statistics.set_file(uploaded_file)

    st.session_state.logs_table_obj = statistics.log_table

    st.session_state.mA_statistics_table_obj = statistics.mA_table
    st.session_state.kV_statistics_table_obj = statistics.kV_table
    st.session_state.ms_statistics_table_obj = statistics.ms_table
    st.session_state.failure_statistics_table_obj = statistics.failure_table
    st.session_state.warning_statistics_table_obj = statistics.warning_table
