from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID

class Metadata(BaseModel):
    message_time: datetime
    company_id: UUID
    message_id: UUID

class Data(BaseModel):
    order_id: UUID
    order_time: datetime
    order_amount: float

class Message(BaseModel):
    metadata: Metadata
    data: Data
