from functools import lru_cache

import boto3

from app.config import get_settings

# No access keys here: boto3 finds credentials itself (the EC2 instance role in production).


@lru_cache
def get_s3_client():
    return boto3.client("s3", region_name=get_settings().aws_region)


@lru_cache
def get_table():
    settings = get_settings()
    dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
    return dynamodb.Table(settings.dynamodb_table)
