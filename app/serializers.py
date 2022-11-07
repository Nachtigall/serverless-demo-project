from datetime import date
from pprint import pprint

from marshmallow import Schema, fields


class ScrapeRequestSchema(Schema):
    handle = fields.Str()


class ResponseSchema(Schema):
    handle = fields.Str()
    s3_url = fields.Str()
