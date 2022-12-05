"""File useful to display an special page for Log History Analysis."""

import pandas as pd
import streamlit as st

from common.tables import LogLegendTable, TableInterface


class LogsPage:
    def __init__(self, log_table: LogLegendTable, uploaded_file: str) -> None:
        self._log_table = log_table
        self._uploaded_file = uploaded_file

    def show_page_header(self) -> None:
        st.header("Análise de histórico de logs")

    def show_log_filter(self) -> None:
        self.log_selected = st.selectbox('\nLog sob análise:', self._log_table.get_logs_names())
        if self.log_selected:
            self.log_index_selected = self._log_table.get_log_index_by_name(self.log_selected)
            self.log_table_selected = TableInterface(sheet_name=self.log_index_selected)
            self.log_table_selected.set_file(self._uploaded_file)


    def __special_filter_selection_is_failure(self) -> bool:
        return self.special_filter_selection == "Falha"  

    def __special_filter_selection_is_warning(self) -> bool:
        return self.special_filter_selection == "Warning"  


    def show_failure_warning_special_filter(self) -> None:
        log_dataframe = self.log_table_selected.get_dataframe().astype(str)
        
        # First layer of filtering
        self.special_filter_selection = st.selectbox(
            '\nFiltro especial para Falha e Warning (exibe também a linha anterior à opção selecionada):',
            ["Nenhum", "Falha", "Warning"],
        )
        
        # Second layer of filtering
        if self.__special_filter_selection_is_failure() or self.__special_filter_selection_is_warning():
            rows_list = self.__get_rows_list_from_column(
                log_dataframe, self.special_filter_selection, non_duplicated=True, non_nan=True
            )
            user_msg = 'Filtro de ' + self.special_filter_selection
            self.special_filter_sub_selection = st.selectbox(user_msg, rows_list)
            self.number_of_back_lines = st.number_input('Número de linhas anteriores:', min_value=0, max_value=1, value=1)


    def __get_rows_list_from_column(self, dataframe: pd.DataFrame, column: str, non_duplicated=False, non_nan=False) -> list:
        if non_nan:
            dataframe.dropna(inplace=True)
            dataframe.drop(dataframe[dataframe[column] == " "].index, errors='ignore', inplace = True)
        rows_list = dataframe[column].to_list()
        if non_duplicated:
            rows_list = list(dict.fromkeys(rows_list))
            try:
                rows_list.sort()
            except TypeError:
                pass
        return rows_list
    
    def show_filtered_log_dataframe(self) -> None:
        st.write("\nHistórico do log selecionado")
        
        log_dataframe_original = self.log_table_selected.get_dataframe().astype(str)
        log_dataframe_original_index_list = log_dataframe_original.index.tolist()
        
        log_dataframe = log_dataframe_original.copy()
        
        # 'Falha' or 'Warning
        if self.__special_filter_selection_is_failure() or self.__special_filter_selection_is_warning():
            log_dataframe = log_dataframe[log_dataframe[self.special_filter_selection].isin([self.special_filter_sub_selection])]
            
            filtered_index_list = log_dataframe.index.tolist()
            additional_lines_filtered_index_list = [index-self.number_of_back_lines for index in filtered_index_list]
            
            merged_indexes_list = []
            merged_indexes_list.extend(filtered_index_list)
            merged_indexes_list.extend(additional_lines_filtered_index_list)
            merged_indexes_list.sort()
            
            merged_indexes_list = [index for index in merged_indexes_list if index in log_dataframe_original_index_list]
            
            log_dataframe = log_dataframe_original[log_dataframe_original.index.isin(merged_indexes_list)]
            
        st.write(log_dataframe)


    def show_page(self) -> None:
        self.show_page_header()
        self.show_log_filter()
        self.show_failure_warning_special_filter()
        self.show_filtered_log_dataframe()
