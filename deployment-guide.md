# Deployment Guide

### Prerequisites

- AWS CLI configured with IAM credentials.
- SAM CLI installed.
- Python 3.9+ and virtual environment ready.


### Deployment Steps

1. **Clone and Build**
   ```bash
   git clone https://github.com/.../message-processing-system.git
   cd message-processing-system
   sam build
    ```

2. **Deploy**
   ```bash
    sam deploy --guided
    ```
- Provide stack name (message-processing-system).
- Select AWS region.
- Save configuration to samconfig.toml for future runs.


3. **Verify Resources**
After deployment:
- Check API URL in terminal output.
- Confirm DynamoDB table created.
- Confirm S3 bucket exists.


4. **Test API**
Use curl or Postman to send sample POST and GET requests.



### Rollback

```bash
aws cloudformation delete-stack --stack-name message-processing-system
```

### Logs
To view logs:
```bash
sam logs -n PostMessageFunction --stack-name message-processing-system
```
