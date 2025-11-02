import os
import json
import logging
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from utils.validation_utils import validate_message_payload
from services.s3_service import save_message_json
from services.dynamodb_service import put_message_if_not_exists
from utils.response_utils import make_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def serialize_for_dynamodb(obj):
    if isinstance(obj, dict):
        return {k: serialize_for_dynamodb(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_dynamodb(v) for v in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj


def lambda_handler(event, context):
    body_raw = event.get("body")
    if not body_raw:
        return make_response(400, {"error": "Empty body"})

    try:
        payload = json.loads(body_raw)
    except json.JSONDecodeError:
        return make_response(400, {"error": "Invalid JSON"})

    msg, errors = validate_message_payload(payload)
    if errors:
        logger.warning("Validation failed", extra={"errors": errors, "payload": payload})
        return make_response(400, {"error": "validation_failed", "details": errors})

    company_id = str(msg.metadata.company_id)
    message_id = str(msg.metadata.message_id)

    data_dict = serialize_for_dynamodb(msg.data.model_dump())
    metadata_dict = serialize_for_dynamodb(msg.metadata.model_dump())

    try:
        s3_key = save_message_json(payload)
    except Exception as exc:
        logger.exception("Failed to save message to S3")
        return make_response(500, {"error": "s3_error", "message": str(exc)})

    try:
        saved = put_message_if_not_exists(company_id, message_id, metadata_dict, data_dict, s3_key)
    except Exception as exc:
        logger.exception("Failed to save metadata to DynamoDB")
        return make_response(500, {"error": "dynamodb_error", "message": str(exc)})

    if not saved:
        return make_response(200, {"status": "duplicate", "message_id": message_id, "s3_key": s3_key})

    return make_response(201, {"status": "stored", "message_id": message_id, "s3_key": s3_key})
