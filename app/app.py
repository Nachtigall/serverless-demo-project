import os
from io import BytesIO
from random import randint

import boto3
import requests
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from browser import Driver
from bs4 import BeautifulSoup
from env_variables import (bucket_name, default_max_items, dynamodb_client,
                           s3_client, table)
from flask import Flask, jsonify, make_response, request
from marshmallow import ValidationError
from serializers import ResponseSchema, ScrapeRequestSchema

import serverless_wsgi

request_schema = ScrapeRequestSchema()
response_schema = ResponseSchema()

app = Flask(__name__)


@app.route("/scrape", methods=["POST"])
def scrape_user():
    try:
        request_data = request_schema.load(request.json)
    except ValidationError as err:
        return make_response(jsonify(message=err.messages), 400)

    handle = request_data["handle"]

    driver = Driver()
    data = driver.scrape_data(f"https://twitter.com/{handle}")

    soup = BeautifulSoup(data, "html.parser")

    if "Page not found" in soup.title.string:
        return make_response(jsonify(message="Looks like user is not found"), 404)

    try:
        img_url = soup.find("img", attrs={"alt": "Opens profile photo"}).get("src")
    except AttributeError:
        return make_response(
            jsonify(
                message="Looks like Twitter didn't like our headless browser. Can you try one more time?"
            ),
            400,
        )

    file_name = f"{handle}.jpg"

    try:
        with requests.get(img_url, stream=True) as f:
            data = s3_client.upload_fileobj(f.raw, bucket_name, file_name)
    except ClientError as err:
        return make_response(jsonify(message=err), 500)

    url = s3_client.generate_presigned_url(
        "get_object", Params={"Bucket": bucket_name, "Key": file_name}, ExpiresIn=604800
    )

    final_results = {"handle": handle, "s3_url": url}

    table.put_item(Item=final_results)

    return jsonify(message=response_schema.dump(final_results))


@app.route("/users", methods=["GET"])
def get_all_user():
    data = list()

    pagination_config = {
        "MaxItems": default_max_items,
    }

    next_token = request.args.get("next_token", None)

    if next_token:
        pagination_config["StartingToken"] = next_token

    paginator = dynamodb_client.get_paginator("scan")
    page_iterator = paginator.paginate(
        TableName=os.environ["DYNAMODB_TABLE"], PaginationConfig=pagination_config
    ).build_full_result()

    for item in page_iterator["Items"]:
        data.append({"handle": item["handle"]["S"], "s3_url": item["s3_url"]["S"]})

    return jsonify(
        message=response_schema.dump(data, many=True),
        next_token=page_iterator.get("NextToken", None),
    )


@app.route("/user/<string:handle>/profile_pic", methods=["GET"])
def get_user(handle: str):
    result = table.query(KeyConditionExpression=Key("handle").eq(handle))

    return jsonify(message=response_schema.dump(result["Items"], many=True))


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error="Not found!"), 404)


def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)
