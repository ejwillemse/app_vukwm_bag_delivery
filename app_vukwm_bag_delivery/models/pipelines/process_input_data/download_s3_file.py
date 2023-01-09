import json
import logging
import os
from typing import Dict

import boto3
import pandas as pd
import toml


def get_s3_bucket_session(s3_cred: Dict[str, str], bucket: str):
    aws_access_key_id = s3_cred["aws_access_key_id"]
    aws_secret_access_key = s3_cred["aws_secret_access_key"]
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    s3 = session.resource("s3")
    my_bucket = s3.Bucket(bucket)
    return my_bucket


def download_file(my_bucket, s3_path, local_path):
    if not os.path.isdir(local_path[: local_path.rfind("/") + 1]):
        os.makedirs(local_path[: local_path.rfind("/")])
    key = s3_path
    upload = local_path
    if os.path.isfile(local_path):
        logging.info(f"File {key} already downloaded to {upload}")
    else:
        try:
            my_bucket.download_file(key, upload)
        except:
            logging.error(f"Could not download {key} to {upload}")
            raise ValueError("failure")


def get_latest_bucket_files(my_bucket, prefix: str) -> pd.DataFrame:
    existing_s3_files = my_bucket.objects.filter(Prefix=prefix)
    pulled_results = []
    for key in existing_s3_files:
        pulled_results.append(
            {"filename": key.key, "size": key.size, "last_modified": key.last_modified}
        )
    file_info = pd.DataFrame(pulled_results)
    return file_info


def download_return_latest_file(my_bucket, file_info, driver):
    latest_file = file_info.sort_values(["last_modified"], ascending=False).iloc[0][
        "filename"
    ]
    download_file(my_bucket, latest_file, "data/" + latest_file)
    return driver("data/" + latest_file)


def read_json_file(file_name: str):
    """Readd single test file"""
    with open(file_name, mode="r", encoding="utf-8") as file:
        return json.load(file)


def return_routing_files(
    bucket,
    s3_cred,
    excel_prefix_path,
    geocoded_prefix_path,
    unassgined_stops_prefix_path,
):
    my_bucket = get_s3_bucket_session(s3_cred, bucket)

    excel_files = get_latest_bucket_files(my_bucket, excel_prefix_path)
    latest_excel_file = download_return_latest_file(
        my_bucket, excel_files, pd.read_excel
    )

    geo_files = get_latest_bucket_files(my_bucket, geocoded_prefix_path)
    latest_geo_file = download_return_latest_file(my_bucket, geo_files, pd.read_csv)

    unassigned_stops_files = get_latest_bucket_files(
        my_bucket, unassgined_stops_prefix_path
    )
    latest_unassigned_stops_file = download_return_latest_file(
        my_bucket, unassigned_stops_files, read_json_file
    )
    return latest_excel_file, latest_geo_file, latest_unassigned_stops_file
