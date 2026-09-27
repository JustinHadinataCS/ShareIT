from types import SimpleNamespace

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from app.aws import get_s3_client, get_table
from app.config import get_settings
from app.main import app

REGION = "us-east-1"
BUCKET = "test-bucket"
TABLE = "test-shares"
CACHED = (get_settings, get_s3_client, get_table)


@pytest.fixture
def aws(monkeypatch, tmp_path):
    # Keep your real AWS profile, keys and backend/.env out of the tests.
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_REGION", REGION)
    monkeypatch.setenv("S3_BUCKET", BUCKET)
    monkeypatch.setenv("DYNAMODB_TABLE", TABLE)
    monkeypatch.setenv("PUBLIC_URL", "http://testserver")

    # Settings and boto3 clients are cached, so rebuild them for every test.
    for cached in CACHED:
        cached.cache_clear()

    with mock_aws():
        s3 = boto3.client("s3", region_name=REGION)
        s3.create_bucket(Bucket=BUCKET)
        table = boto3.resource("dynamodb", region_name=REGION).create_table(
            TableName=TABLE,
            KeySchema=[{"AttributeName": "share_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "share_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield SimpleNamespace(s3=s3, bucket=BUCKET, table=table)

    for cached in CACHED:
        cached.cache_clear()


@pytest.fixture
def client(aws):
    return TestClient(app)
