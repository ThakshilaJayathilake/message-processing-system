import os
import time
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
import json


def _table():
    TABLE_NAME = os.environ.get("DDB_TABLE")
    if not TABLE_NAME:
        raise RuntimeError("DDB_TABLE is not set")
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    return dynamodb.Table(TABLE_NAME)

def put_message_if_not_exists(company_id: str, message_id: str, metadata: dict, data: dict, s3_key: str) -> bool:
    item = {
        "company_id": company_id,
        "message_id": message_id,
        "metadata": metadata,
        "data": data,
        "s3_key": s3_key,
        "created_at": int(time.time())
    }

    table = _table()
    try:
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(company_id) AND attribute_not_exists(message_id)"
        )
        return True
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code == "ConditionalCheckFailedException":
            return False
        raise

def get_message(company_id: str, message_id: str) -> dict:
    resp = _table().get_item(Key={"company_id": company_id, "message_id": message_id})
    return resp.get("Item")
