# Message Processing System

A serverless system built on **AWS Lambda**, **API Gateway**, **DynamoDB**, and **S3** to process, validate, and store messages sent by external clients.  
This project is deployed using **AWS SAM (Serverless Application Model)**.

---

## Features

- **POST /messages** – Validate and store message payloads
- **GET /messages/{id}** – Retrieve message metadata and full payload
- **Data Storage** – Metadata in DynamoDB, raw JSON in S3
- **Duplicate Detection** – Avoids inserting messages with same ID twice
- **Error Handling** – Returns proper JSON errors with structured messages
- **Logging** – Centralized in CloudWatch

---

## Architecture Summary

Client
↓
API Gateway
↓
Lambda (POST/GET handlers)
↓
├─ DynamoDB → stores metadata
└─ S3 → stores raw message JSON


**DynamoDB Table:**  
- Partition Key: `company_id`  
- Sort Key: `message_id`

**S3 Structure:**  
- `s3://message-processing-bucket/{company_id}/{message_id}.json`


## Setup

### Prerequisites
- AWS CLI configured with valid credentials
- AWS SAM CLI installed
- Python 3.9+

### Local Run
```bash
sam build
sam local start-api
```

### Deploy to AWS
```bash
sam deploy --guided
```

After deployment, SAM will output API Gateway URLs for POST and GET endpoints.

## Example Requests

### POST /messages
```bash
curl -X POST https://{api-id}.execute-api.{region}.amazonaws.com/dev/messages \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": { "company_id": "X001", "message_id": "M1001", "message_time": "2025-10-19T09:00:00Z" },
    "data": { "order_id": "O789", "order_time": "2025-10-19T09:00:00Z", "price": 150.25 }
  }'
```

### GET /messages/{message_id}
```bash
curl https://{api-id}.execute-api.{region}.amazonaws.com/dev/messages/M1001?company_id=X001
```
