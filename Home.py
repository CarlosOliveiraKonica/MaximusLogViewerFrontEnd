import streamlit as st

from common.tables import StatisticsTables


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
