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

from app_vukwm_bag_delivery.dispatch_routes.excel_download import format_routes
from app_vukwm_bag_delivery.models.pipelines.process_input_data import \
    download_s3_file

log = logging.getLogger(__name__)


def get_session_state():
    output_dict = {}
    keys = st.session_state.keys()
    for key in keys:
        output = st.session_state[key]
        if key == "data_04_model_input":
            output_store = {x: output[x] for x in output if x != "vroom_input"}
        elif key == "data_06_model_output":
            output_store = {
                x: output[x]
                for x in output
                if x not in ["vroom_output", "vroom_solution"]
            }
        else:
            output_store = output
        try:
            output_dict[key] = deepcopy(output_store)
        except:
            st.error("Something went wrong with saving the session state")
            return None
    return output_dict


def get_s3_bucket_session(s3_cred: Dict[str, str]):
    aws_access_key_id = s3_cred["aws_access_key_id"]
    aws_secret_access_key = s3_cred["aws_secret_access_key"]
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    s3_resource = session.resource("s3")
    return s3_resource


def write_local(filename):
    session_state = get_session_state()
    if session_state is not None:
        with open("data/00_session_state/" + filename, "wb") as f:
            pickle.dump(get_session_state(), f)


def upload_st_session_state(
    s3_cred: Dict[str, str],
    filename: str,
):
    if st.secrets["local_dev"] is True:
        write_local(filename)
        return None
    s3_resource = get_s3_bucket_session(s3_cred)
    bucket = st.secrets["bucket"]
    s3_path = st.secrets["s3_input_paths"]["session_files"]
    path = s3_path + filename
    log.info(f"Uploading file to {path}")
    pickle_byte_obj = pickle.dumps(get_session_state())
    s3_resource.Object(bucket, path).put(Body=pickle_byte_obj)
    log.info(f"Uploading session {filename} successfull")


def generate_filename(session_note):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    user = st.session_state["username"]
    return f"session_{timestamp}__user:{user}__Note:{session_note}.pickle"


def upload_to_session_bucket(session_note):
    filename = generate_filename(session_note)
    s3_cred = st.secrets["dev_s3"]
    upload_st_session_state(
        s3_cred,
        filename=filename,
    )


def save_session():
    session_note = st.sidebar.text_input("Session notes", value="")
    st.sidebar.button(
        "Save session", on_click=upload_to_session_bucket, args=(session_note,)
    )
