import streamlit as st

from common.tables import StatisticsTables
from common.page_body import StatisticsPage, LogsPage


st.set_page_config(page_title="MaximusLogViewer", layout="wide")

st.write('# MaximusLogViewer')

uploaded_file = st.file_uploader('Selecione o arquivo EXCEL exportado pelo script do MaximusLogViewer:', type=[".xlsx"])

if uploaded_file:
    st.write(uploaded_file.name)
    
    statistics = StatisticsTables()
    statistics.set_file(uploaded_file)

    mA_tab, kV_tab, ms_tab, failure_tab, warning_tab, exposition_tab, logs_tab = st.tabs(
        ["mA", "kV", "ms", "Falha", "Warning", "Exposição", "Logs"]
    )
    
    with mA_tab:
        mA_page = StatisticsPage(
            statistics.mA_table,
            statistics.log_table,
        )
        mA_page.show_log_filter()
        mA_page.show_key_column_multi_select_filter(
            valid_selection_list=[10, 50, 100, 125, 160, 220, 280, 320, 360, 400, 450, 500, 630, 800]
        )
        mA_page.show_log_and_statistics_table()
        mA_page.show_bar_chart()
        mA_page.show_pie_chart()

    with kV_tab:
        kV_page = StatisticsPage(
            statistics.kV_table,
            statistics.log_table,
        )
        kV_page.show_log_filter()
        kV_page.show_key_column_range_select_filter(
            valid_range_min=40,
            valid_range_max=150,
        )
        kV_page.show_log_and_statistics_table()
        kV_page.show_bar_chart()
        kV_page.show_pie_chart()

    with ms_tab:
        ms_page = StatisticsPage(
            statistics.ms_table,
            statistics.log_table,
        )
        ms_page.show_log_filter()
        ms_page.show_key_column_range_select_filter(
            valid_range_min=1,
            valid_range_max=5000,
        )
        ms_page.show_log_and_statistics_table()
        ms_page.show_bar_chart()
        ms_page.show_pie_chart()

    with failure_tab:
        failure_page = StatisticsPage(
            statistics.failure_table,
            statistics.log_table,
        )
        failure_page.show_log_filter()
        failure_page.show_key_column_multi_select_filter()
        failure_page.show_log_and_statistics_table()
        failure_page.show_bar_chart()
        failure_page.show_pie_chart()

    with warning_tab:
        warning_page = StatisticsPage(
            statistics.warning_table,
            statistics.log_table,
        )
        warning_page.show_log_filter()
        warning_page.show_key_column_multi_select_filter()
        warning_page.show_log_and_statistics_table()
        warning_page.show_bar_chart()
        warning_page.show_pie_chart()

    with exposition_tab:
        exposition_page = StatisticsPage(
            statistics.exposition_table,
            statistics.log_table,
        )
        exposition_page.show_log_filter()
        exposition_page.show_column_multi_select_filter(
            "mA",
            valid_selection_list=[10, 50, 100, 125, 160, 220, 280, 320, 360, 400, 450, 500, 630, 800],
        )
        exposition_page.show_column_range_select_filter(
            "kV",
            valid_range_min=40,
            valid_range_max=150,
        )
        exposition_page.show_column_range_select_filter(
            "ms",
            valid_range_min=1,
            valid_range_max=5000,
        )
        exposition_page.show_log_and_statistics_table()

    with logs_tab:
        logs_page = LogsPage(
            statistics.log_table,
            uploaded_file,
        )
        logs_page.show_log_filter()
