import datetime
import json
import logging
import os
from io import StringIO
from typing import Dict

import boto3
import pandas as pd
import toml

# boto3 upload file to s3 bucket using session


def upload_file(
    df: pd.DataFrame,
    s3_cred: Dict[str, str],
    s3_path: str,
    filename: str | None = None,
):
    aws_access_key_id = s3_cred["aws_access_key_id"]
    aws_secret_access_key = s3_cred["aws_secret_access_key"]
    if filename is None:
        filename = (
            "dispatch_route_sheet__" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
        )
    path = s3_path + filename
    df.to_csv(
        path,
        storage_options={"key": "aws_access_key_id", "secret": "aws_secret_access_key"},
    )
