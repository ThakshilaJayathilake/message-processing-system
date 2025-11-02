import os
import json
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")

def s3_key_for(company_id: str, message_id: str) -> str:
    return f"{company_id}/{message_id}.json"

def save_message_json(payload: dict) -> str:
    BUCKET_NAME = os.getenv("BUCKET_NAME") 
    if not BUCKET_NAME:
        raise RuntimeError("BUCKET_NAME is not set")
    meta = payload.get("metadata", {})
    company_id = str(meta.get("company_id"))
    message_id = str(meta.get("message_id"))
    key = s3_key_for(company_id, message_id)
    body = json.dumps(payload).encode("utf-8")
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=body)
        return key
    except ClientError as exc:
        raise
