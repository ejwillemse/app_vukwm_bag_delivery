import datetime
from io import BytesIO

import pandas as pd
import streamlit as st


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Sheet1")
    for column in df:
        column_width = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets["Sheet1"].set_column(col_idx, col_idx, column_width)
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def download_results():
    assigned_jobs = st.session_state.data_07_reporting["assigned_jobs_download"]
    df_xlsx = to_excel(assigned_jobs)
    return df_xlsx
