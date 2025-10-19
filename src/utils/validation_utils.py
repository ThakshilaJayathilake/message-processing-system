from pydantic import ValidationError
from models.message_model import Message

def validate_message_payload(payload: dict):
    try:
        msg = Message.parse_obj(payload)
        return msg, None
    except ValidationError as exc:
        return None, exc.errors()
