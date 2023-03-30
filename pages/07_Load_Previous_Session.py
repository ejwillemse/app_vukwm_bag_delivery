import io
import logging
import os
import pickle
from copy import deepcopy
from datetime import datetime
from io import StringIO
from typing import Dict

import boto3
import pandas as pd
import streamlit as st

import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.dispatch_routes.excel_download import format_routes
from app_vukwm_bag_delivery.models.pipelines.process_input_data import download_s3_file
from app_vukwm_bag_delivery.util_presenters.check_password import check_password

log = logging.getLogger(__name__)


def return_local_files():
    files = os.listdir("data/00_session_state/")
    return files


def return_s3_files():
    s3_cred = st.secrets["dev_s3"]
    bucket = st.secrets["bucket"]
    path = st.secrets["s3_input_paths"]["session_files"]
    my_bucket = download_s3_file.get_s3_bucket_session(s3_cred, bucket)
    files = download_s3_file.get_latest_bucket_files(my_bucket, path)
    if files.shape[0] > 0:
        files = [x.replace(path, "") for x in files["filename"].values]
    else:
        files = None
    return files


def get_session_files():
    today = datetime.today().strftime("%Y-%m-%d")
    limit_today = st.checkbox(f"Only show saved sessions for today: **{today}**", True)
    if st.secrets["local_dev"] is True:
        files = return_local_files()
    else:
        files = return_s3_files()
    if len(files) == 0:
        return (
            None,
            None,
            None,
        )
    else:
        return files, today, limit_today


def generate_session_file_data_frame(files, today, limit_today):
    files_split = [f.replace(".pickle", "").split("__") for f in files]
    timestamp = [f[0].replace("session_", "").split("_") for f in files_split]
    date = [f[0] for f in timestamp]
    time = [f[1] for f in timestamp]
    user = [f[1].replace("user:", "") for f in files_split]
    notes = [f[2].replace("Note:", "") for f in files_split]
    file_info = {
        "Selected": [False] * len(files),
        "Date": date,
        "Time": time,
        "User": user,
        "Notes": notes,
        "File": files,
    }
    file_info = (
        pd.DataFrame(file_info)
        .sort_values(["Date", "Time"], ascending=False)
        .reset_index(drop=True)
    )
    if limit_today:
        file_info = file_info[file_info["Date"] == today].copy()
    if file_info.shape[0] == 0:
        return None
    file_info.iloc[0, 0] = True
    return file_info


def confirm_select(selected):
    if selected["Selected"].sum() == 1:
        selected_file = selected[selected["Selected"] == True].iloc[0]["File"]
        pressed = st.button("Load previous session")
        if pressed:
            load_session_info(selected_file)
    elif selected["Selected"].sum() > 1:
        st.warning("Please select only one session to load")


def save_new_session_info(session_info):
    special_keys = ["username", "password_correct"]
    session_state = st.session_state.keys()
    for key in session_state:
        logging.info(f"Inspecting from current session {key}")
        if key not in special_keys and key not in session_info:
            logging.info(f"Deleted {key}")
            del st.session_state[key]
    for key in session_info:
        if key not in special_keys:
            logging.info(f"Loaded {key}")
            st.session_state[key] = session_info[key]


def load_local_session_info(filename):
    PATH = "data/00_session_state/"
    with open(PATH + filename, "rb") as f:
        session_info = pickle.load(f)
    logging.info(f"Loaded session {PATH + filename}")
    return session_info


def load_s3_session_info(filename):
    s3_cred = st.secrets["dev_s3"]
    bucket = st.secrets["bucket"]
    path = st.secrets["s3_input_paths"]["session_files"]
    my_bucket = download_s3_file.get_s3_bucket_session(s3_cred, bucket)
    full_file = path + filename
    session_info = pickle.loads(my_bucket.Object(full_file).get()["Body"].read())
    return session_info


def load_session_info(filename):
    if st.secrets["local_dev"] is True:
        session_info = load_local_session_info(filename)
    else:
        session_info = load_s3_session_info(filename)
    save_new_session_info(session_info)


if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()

side_bar_status = side_bar_progress.view_sidebar()
st.title("Load previous session")
st.write(
    "Select one of the following sessions for loading (note that all the current session info will be over-written):"
)
files, today, limit_today = get_session_files()
session_files = generate_session_file_data_frame(files, today, limit_today)
if session_files is None:
    st.warning("No previous saved sessions found.")
else:
    selected = st.experimental_data_editor(session_files)
    confirm_select(selected)
side_bar_progress.update_side_bar(side_bar_status)
