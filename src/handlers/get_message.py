import os
import json
import logging
from services.dynamodb_service import get_message
from services.s3_service import s3_key_for
from utils.response_utils import make_response
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.client("s3")
BUCKET = os.environ.get("BUCKET_NAME")

def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    qs = event.get("queryStringParameters") or {}

    message_id = path_params.get("message_id")
    company_id = qs.get("company_id")

    if not message_id or not company_id:
        return make_response(400, {"error": "message_id path param and company_id query param required"})

    item = get_message(company_id, message_id)
    if not item:
        return make_response(404, {"error": "not_found"})

    s3_key = item.get("s3_key")
    raw = None
    if s3_key and BUCKET:
        try:
            obj = s3.get_object(Bucket=BUCKET, Key=s3_key)
            raw = obj["Body"].read().decode("utf-8")
            try:
                raw = json.loads(raw)
            except Exception:
                pass
        except Exception:
            logger.warning("Could not fetch raw payload from S3", exc_info=True)

    resp = {
        "company_id": item.get("company_id"),
        "message_id": item.get("message_id"),
        "metadata": item.get("metadata"),
        "data": item.get("data"),
        "s3_key": s3_key,
        "raw": raw
    }
    return make_response(200, resp)
