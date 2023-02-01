import datetime

import gspread
import streamlit as st
from google.oauth2 import service_account

from app_vukwm_bag_delivery.util_views.return_session_status import (
    check_route_sheets_generated,
)


def creat_file_name():
    return f"vukwm_bag_delivery_route_sheet_{datetime.datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss')}"


def return_credentials():
    return service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )


def create_new_route_sheet():
    new_file_name = creat_file_name()
    sheet_id = st.secrets["google-sheet"]["template_sheet_id"]
    gc = gspread.authorize(return_credentials())
    gc.copy(
        sheet_id,
        title=new_file_name,
        copy_permissions=True,
    )
    sh = gc.open(new_file_name)
    return sh, new_file_name


def write_cell_info(sheet, cell_info):
    sheet_values = sheet.get_all_values()
    job_cell_update = (
        [cell_info["summary_info"]] + cell_info["job_cells"] + cell_info["stop_cells"]
    )
    n_row = len(sheet_values)
    max_row = 0
    for update in job_cell_update:
        for key in update:
            (column, row) = key.split(":")
            row = int(row) - 1
            column_index = ord(column.lower()) - 97
            value = update[key]
            sheet_values[row][column_index] = value
            if row > max_row:
                max_row = row
    sheet.update("A1", sheet_values)
    sheet.delete_rows(max_row + 2, n_row + 1)


def write_route_info(sh, sheet_cells):
    for i, vehicle_id in enumerate(sheet_cells.keys()):
        sh.duplicate_sheet(
            sh.worksheet("template").id,
            insert_sheet_index=i + 1,
            new_sheet_name=vehicle_id,
        )
        sheet = sh.worksheet(vehicle_id)
        write_cell_info(sheet, sheet_cells[vehicle_id])


def delete_template_sheet(sh):
    sh.del_worksheet(sh.worksheet("template"))


def write_google_sheet():
    (sh, filename) = create_new_route_sheet()
    sheet_cells = st.session_state.data_07_reporting["route_sheet_cell_values"]
    write_route_info(sh, sheet_cells)
    delete_template_sheet(sh)
    sheet_link = f"https://docs.google.com/spreadsheets/d/{sh.id}/edit#gid=0"
    if not check_route_sheets_generated():
        st.session_state.data_07_reporting["route_sheet_urls"] = []
    st.session_state.data_07_reporting["route_sheet_urls"].append(
        [filename, sheet_link]
    )
