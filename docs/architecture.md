# Architecture

### System Overview
The Message Processing System is a serverless architecture designed to process, validate, and persist incoming message payloads through AWS-managed components. It emphasizes cost efficiency, scalability, and simplicity by avoiding manual infrastructure management.


### Components

#### API Gateway
- Exposes REST endpoints for message ingestion and retrieval.
- Handles routing and CORS.


#### Lambda Functions
1. **PostMessageFunction**
   - Validates incoming JSON structure.
   - Converts unsupported data types (UUID, float, datetime).
   - Saves full message JSON to S3.
   - Inserts structured metadata into DynamoDB.
   - Returns structured HTTP responses.


2. **GetMessageFunction**
   - Fetches metadata from DynamoDB using `company_id` and `message_id`.
   - Optionally reads full JSON from S3.
   - Combines data into a single response object.


#### DynamoDB Table
- Stores metadata and message information.
- Acts as a fast lookup table.
- Schema:
  - `company_id` (PK)
  - `message_id` (SK)
  - Additional attributes: metadata, data, s3_key.


#### S3 Bucket
- Stores raw message JSON files.
- Acts as the source of truth for full message content.
- Key structure: `{company_id}/{message_id}.json`


#### CloudWatch
- Logs for Lambda executions.
- Used for error tracking and performance metrics.


### Data Flow
1. Client sends POST request with JSON payload.
2. API Gateway forwards to PostMessage Lambda.
3. Lambda validates → stores in S3 → writes metadata to DynamoDB.
4. GET request retrieves from DynamoDB and optionally reads from S3.


### Security
- IAM roles with least privilege for Lambda.
- S3 bucket private by default.
- DynamoDB access restricted to function role.
- Logging centralized in CloudWatch.


### Future Enhancements
- DLQ for failed messages.
- API Gateway authorizer for authentication.
- CI/CD pipeline integration with GitHub Actions.
- CloudWatch alarms for operational health.