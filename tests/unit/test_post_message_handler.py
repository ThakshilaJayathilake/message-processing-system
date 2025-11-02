import json
import pytest
from moto import mock_aws 
import boto3
from src.handlers import post_message
from uuid import uuid4
import os
import importlib

@pytest.fixture()
def aws_env(monkeypatch):
    monkeypatch.setenv("DDB_TABLE", "test-messages-table")
    monkeypatch.setenv("BUCKET_NAME", "test-messages-bucket")

@mock_aws
def test_post_message_valid_payload(aws_env):
    os.environ["BUCKET_NAME"] = "test-messages-bucket"
    os.environ["DDB_TABLE"] = "test-messages-table"
    # Mock AWS services
    dynamo = boto3.resource("dynamodb", region_name="us-east-1")
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-messages-bucket")

    dynamo.create_table(
        TableName="test-messages-table",
        KeySchema=[
            {"AttributeName": "company_id", "KeyType": "HASH"},
            {"AttributeName": "message_id", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "company_id", "AttributeType": "S"},
            {"AttributeName": "message_id", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST"
    )

    table = dynamo.Table("test-messages-table")
    table.wait_until_exists()

    # Reload the dynamodb_service AFTER mocks are active
    import src.services.dynamodb_service as dynamodb_service
    importlib.reload(dynamodb_service)

    # Now reload post_message to ensure it uses the mocked service
    importlib.reload(post_message)

    body = {
        "metadata": {
            "company_id": str(uuid4()),
            "message_id": str(uuid4()),
            "message_time": "2025-10-19T10:00:00Z"
        },
        "data": {
            "order_id": str(uuid4()),
            "order_time": "2025-10-19T10:00:00Z",
            "order_amount": 10.5
        }
    }

    event = {"body": json.dumps(body)}

    response = post_message.lambda_handler(event, None)
    assert response["statusCode"] in [200, 201]

# Empty body test
def test_post_message_empty_body(aws_env):
    event = {"body": ""}
    response = post_message.lambda_handler(event, None)
    assert response["statusCode"] == 400

# Invalid JSON test
def test_post_message_invalid_json(aws_env):
    event = {"body": "{invalid_json"}
    response = post_message.lambda_handler(event, None)
    assert response["statusCode"] == 400

# Missing metadata fields
def test_post_message_missing_metadata(aws_env):
    event = {"body": json.dumps({"data": {"order_id": "ORD01"}})}
    response = post_message.lambda_handler(event, None)
    assert response["statusCode"] == 400
