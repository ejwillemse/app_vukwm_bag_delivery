import logging
from datetime import datetime
from io import StringIO
from typing import Dict

import boto3
import pandas as pd
import streamlit as st

from app_vukwm_bag_delivery.dispatch_routes.excel_download import format_routes

log = logging.getLogger(__name__)


def get_s3_bucket_session(s3_cred: Dict[str, str]):
    aws_access_key_id = s3_cred["aws_access_key_id"]
    aws_secret_access_key = s3_cred["aws_secret_access_key"]
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    s3_resource = session.resource("s3")
    return s3_resource


def upload_file(
    df: pd.DataFrame,
    s3_cred: Dict[str, str],
    filename: str | None = None,
):
    s3_resource = get_s3_bucket_session(s3_cred)
    bucket = s3_cred["bucket"]
    s3_path = s3_cred["s3_path"]
    if filename is None:
        filename = (
            "dispatch_route_sheet__" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
        )
    path = s3_path + filename
    log.info(f"Uploading file to {path}")
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    s3_resource.Object(bucket, path).put(Body=csv_buffer.getvalue())
    log.info(f"Uploading successfull")


def upload_to_dispatch_bucket():
    assigned_jobs = format_routes()
    s3_cred = st.secrets["veolia_prod_s3"]
    upload_file(assigned_jobs, s3_cred)
