import json
import boto3
import os

# === CONFIG ===

# SNS Topic ARN - you can use an environment variable or hard-code for testing
SNS_TOPIC_ARN = os.getenv(
    'SNS_TOPIC_ARN',
    'arn:aws:sns:eu-central-1:569836997621:RDSClusterProvisioningTopic'
)

# Boto3 SNS client
sns_client = boto3.client('sns')

# === API Gateway Lambda ===

def lambda_handler(event, context):
    print("Received event from API Gateway:", json.dumps(event))

    try:
        # API Gateway Proxy integration: body is in event['body']
        body = json.loads(event['body'])

        # Basic input validation
        database_name = body.get('database_name')
        database_engine = body.get('database_engine')
        environment = body.get('environment')

        if not database_name or not database_engine or not environment:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required parameters"})
            }

        # Build message payload
        message = {
            "database_name": database_name,
            "database_engine": database_engine,
            "environment": environment
        }

        # Publish to SNS Topic
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message)
        )

        print("Published to SNS. Message ID:", response['MessageId'])

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Request accepted",
                "sns_message_id": response['MessageId']
            })
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


# === SQS Queue Consumer Lambda ===

def sqs_handler(event, context):
    print("Received event from SQS:", json.dumps(event))

    for record in event['Records']:
        body = record['body']
        print("Message body:", body)

        # Here you could:
        # - Parse the message
        # - Trigger a GitHub PR
        # - Call a Terraform pipeline
        # - Handle errors, retries, etc.

    print("Finished processing SQS messages.")
