import json
import os
import boto3
import datetime
from github import Github

# === CONFIG ===

# SNS Topic ARN - from environment variable or fallback
SNS_TOPIC_ARN = os.getenv(
    'SNS_TOPIC_ARN',
    'arn:aws:sns:eu-central-1:569836997621:RDSClusterProvisioningTopic'
)

def get_github_token():
    secret_id = os.getenv("GITHUB_SECRET_ID", "github-token")
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_id)
    secret = json.loads(response['SecretString'])
    return secret['token']


# GitHub Token & Repo Name for creating PRs
GITHUB_TOKEN = get_github_token()
REPO_NAME = os.getenv("REPO_NAME", "shimon23/serverless-rds-cluster-automation")

# Boto3 SNS client
sns_client = boto3.client('sns')


# === API Gateway Lambda ===

def lambda_handler(event, context):
    """
    Handles requests from API Gateway.
    Publishes a message to SNS with the requested DB details.
    """
    print("Received event from API Gateway:", json.dumps(event))

    try:
        # Parse body from API Gateway proxy integration
        body = json.loads(event['body'])

        # Validate required parameters
        database_name = body.get('database_name')
        database_engine = body.get('database_engine')
        environment = body.get('environment')

        if not database_name or not database_engine or not environment:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required parameters"})
            }

        # Build the SNS message payload
        message = {
            "database_name": database_name,
            "database_engine": database_engine,
            "environment": environment
        }

        # Publish message to SNS Topic
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
    """
    Consumes messages from SQS.
    Creates a GitHub Pull Request with Terraform changes for each message.
    """
    print("Received event from SQS:", json.dumps(event))

    # Initialize GitHub connection
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    for record in event['Records']:
        body = json.loads(record['body'])
        print("SQS Message Body:", body)

        db_name = body.get("database_name", "exampledb")
        db_engine = body.get("database_engine", "mysql")
        environment = body.get("environment", "dev")
       
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        branch_name = f"create-{db_name}-instance-{timestamp}"

        # Create new branch from main
        source = repo.get_branch("main")
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)
        print(f"Created branch: {branch_name}")

        # Generate Terraform content
        tf_content = f"""
                    resource "aws_db_instance" "{db_name}" {{
                    identifier              = "{db_name}-instance"
                    allocated_storage       = 20
                    engine                  = "{db_engine}"
                    engine_version          = "8.0"
                    instance_class          = "db.t3.micro"
                    db_name                 = "{db_name}"
                    username                = "admin"
                    password                = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["rds-master-password"]
                    skip_final_snapshot     = true
                    publicly_accessible     = true

                    tags = {{
                        Name        = "{db_name}-instance"
                        Environment = "{environment}"
                    }}
                    }}
                    """

        # Create the Terraform file in the new branch
        repo.create_file(
            path=f"terraform/{db_name}-main.tf",
            message=f"Add Terraform for {db_name}",
            content=tf_content,
            branch=branch_name
        )
        print(f"Created Terraform file for {db_name}")

        # Create Pull Request
        pr = repo.create_pull(
            title=f"Provision RDS for {db_name}",
            body="Auto-created by Lambda!",
            head=branch_name,
            base="main"
        )
        print(f"Pull Request created: {pr.html_url}")

    print("Finished processing all SQS messages.")
