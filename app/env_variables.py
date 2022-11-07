import os

import boto3

IS_OFFLINE = os.environ.get("IS_OFFLINE")

if IS_OFFLINE:
    dynamodb = boto3.resource(
        "dynamodb", region_name="localhost", endpoint_url="http://localhost:8000"
    )
    s3_client = boto3.client(
        "s3",
        endpoint_url="http://localhost:4569",
        aws_access_key_id="S3RVER",
        aws_secret_access_key="S3RVER",
    )
    docker_browser = False
    dynamodb_client = boto3.client(
        "dynamodb", region_name="localhost", endpoint_url="http://localhost:8000"
    )
else:
    dynamodb = boto3.resource("dynamodb")
    s3_client = boto3.client("s3")
    dynamodb_client = boto3.client("dynamodb")
    docker_browser = True

table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])
bucket_name = os.environ["S3_BUCKET"]
default_max_items = 3