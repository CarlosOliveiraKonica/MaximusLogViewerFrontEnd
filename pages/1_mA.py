import streamlit as st

from common.page_body import StatisticsPage

statistics_page = StatisticsPage(
    st.session_state.mA_statistics_table_obj,
    st.session_state.logs_table_obj,
)

statistics_page.show_log_filter()
statistics_page.show_key_column_multi_select_filter()
statistics_page.show_log_and_statistics_table()
statistics_page.show_bar_chart()
statistics_page.show_pie_chart()
