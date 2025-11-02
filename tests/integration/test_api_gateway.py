import os
import boto3
import pytest
import requests
import uuid
import datetime

class TestMessageProcessingAPI:

    @pytest.fixture(scope="session")
    def api_gateway_url(self):
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise ValueError("Set AWS_SAM_STACK_NAME to your deployed stack name")

        client = boto3.client("cloudformation")
        response = client.describe_stacks(StackName=stack_name)
        outputs = response["Stacks"][0]["Outputs"]
        api_output = next(o for o in outputs if o["OutputKey"] == "ApiUrl")
        return api_output["OutputValue"]

    def test_post_and_get_message(self, api_gateway_url):
        post_url = f"{api_gateway_url}messages"
        payload = {
            "metadata": {
                "company_id": "e0721e56-fb09-4273-ae74-7bcbc92d43eb",
                "message_id": str(uuid.uuid4()),
                "message_time": datetime.datetime.utcnow().isoformat() + "Z"
            },
            "data": {
                "order_id": str(uuid.uuid4()),
                "order_time": datetime.datetime.utcnow().isoformat() + "Z",
                "order_amount": 20.5
            }
        }

        post_resp = requests.post(post_url, json=payload)
        assert post_resp.status_code in [200, 201]

        get_url = f"{api_gateway_url}messages/{payload['metadata']['message_id']}?company_id={payload['metadata']['company_id']}"
        get_resp = requests.get(get_url)
        assert get_resp.status_code == 200
        assert get_resp.json()["metadata"]["company_id"] == payload["metadata"]["company_id"]
