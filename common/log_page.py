import streamlit as st

from common.tables import LogLegendTable, TableInterface

class LogsPage:
    def __init__(self, log_table: LogLegendTable, uploaded_file: str) -> None:
        self._log_table = log_table
        self._uploaded_file = uploaded_file

    def show_page_header(self) -> None:
        st.header("Análise de histórico de logs")

    def show_log_filter(self) -> None:
        log_selected = st.selectbox('\nLogs sob análise:', self._log_table.get_logs_names())
        if log_selected:
            log_index_selected = self._log_table.get_log_index_by_name(log_selected)
            log_table_selected = TableInterface(sheet_name=log_index_selected)
            log_table_selected.set_file(self._uploaded_file)
            st.write("\nHistórico do log selecionado")
            st.write(log_table_selected.get_dataframe().astype(str))

    def show_page(self) -> None:
        self.show_page_header()
        self.show_log_filter()
