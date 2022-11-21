"""This is the main file of the project."""

import streamlit as st

from common.tables import StatisticsTables
from common.log_page import LogsPage
from common.log_statistics_page import (
    mA_StatisticsPage,
    kV_StatisticsPage,
    ms_StatisticsPage,
    Failure_StatisticsPage,
    Warning_StatisticsPage,
    Exposition_StatisticsPage,
)


st.set_page_config(page_title="MaximusLogViewer", layout="wide")

st.write('# MaximusLogViewer')

uploaded_file = st.file_uploader('Selecione o arquivo EXCEL exportado pelo script do MaximusLogViewer:', type=[".xlsx"])

if uploaded_file:
    st.write(uploaded_file.name)
    
    statistics = StatisticsTables()
    statistics.set_file(uploaded_file)

    log_analysis_tab, statistics_tab = st.tabs(["Análise de Logs", "Estatísticas"])
    
    with log_analysis_tab:
        logs_page = LogsPage(statistics.log_table, uploaded_file)
        logs_page.show_page()
    
    with statistics_tab:    
    
        mA_tab, kV_tab, ms_tab, failure_tab, warning_tab, exposition_tab = st.tabs(
            ["mA", "kV", "ms", "Falha", "Warning", "Exposição"]
        )
    
        with mA_tab:
            mA_page = mA_StatisticsPage(statistics.mA_table, statistics.log_table)
            mA_page.show_page()

        with kV_tab:
            kV_page = kV_StatisticsPage(statistics.kV_table, statistics.log_table)
            kV_page.show_page()

        with ms_tab:
            ms_page = ms_StatisticsPage(statistics.ms_table, statistics.log_table)
            ms_page.show_page()

        with failure_tab:
            failure_page = Failure_StatisticsPage(statistics.failure_table, statistics.log_table)
            failure_page.show_page()

        with warning_tab:
            warning_page = Warning_StatisticsPage(statistics.warning_table, statistics.log_table)
            warning_page.show_page()

        with exposition_tab:
            exposition_page = Exposition_StatisticsPage(statistics.exposition_table, statistics.log_table)
            exposition_page.show_page()
