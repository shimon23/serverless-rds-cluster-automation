import json
import os
import boto3
import datetime
import logging
from github import Github

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# === Configuration ===

def get_github_token():
    secret_id = os.getenv("GITHUB_SECRET_ID", "github-token")
    if not secret_id:
        raise EnvironmentError("Missing GITHUB_SECRET_ID environment variable.")
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_id)
    secret = json.loads(response["SecretString"])
    return secret["token"]

# Environment Variables
GITHUB_TOKEN = get_github_token()
REPO_NAME = os.getenv("REPO_NAME")
if not REPO_NAME:
    raise EnvironmentError("Missing REPO_NAME environment variable.")

sns_client = boto3.client("sns")

def get_instance_class(env_value):
    """Maps environment name to appropriate instance class."""
    env = env_value.strip().lower()
    mapping = {
        "dev": "db.t3.micro",
        "development": "db.t3.micro",
        "prod": "db.t3.medium",
        "production": "db.t3.medium"
    }
    return mapping.get(env, "db.t3.medium")


def get_engine_version(db_engine):
    db_engine = db_engine.strip().lower()
    if  db_engine == "mysql":
        return "8.0"
    elif db_engine == "postgres":
        return "15.4"
    else:
        raise ValueError(f"Unsupported engine: {db_engine}")

def generate_tf_content(db_name, db_engine, engine_version, instance_class, environment):
    """Returns Terraform code as a string."""
    return f"""
    resource "aws_db_instance" "{db_name}" {{
      identifier              = "{db_name}-instance"
      allocated_storage       = 20
      engine                  = "{db_engine}"
      engine_version          = "{engine_version}"
      instance_class          = "{instance_class}"
      db_name                 = "{db_name}"
      username                = "rdsuser"
      password                = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["rds-master-password"]
      skip_final_snapshot     = true
      publicly_accessible     = true

      tags = {{
        Name        = "{db_name}-instance"
        Environment = "{environment}"
      }}
    }}
    """.strip()

def create_branch(repo, branch_name, base_branch="main"):
    source = repo.get_branch(base_branch)
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)

# === Lambda Handlers ===

def lambda_handler(event, context):
    """Handles incoming API requests."""
    logger.info("Received event from API Gateway: %s", json.dumps(event))
    sns_topic_arn = os.getenv("SNS_TOPIC_ARN")
    if not sns_topic_arn:
        raise EnvironmentError("Missing SNS_TOPIC_ARN environment variable.")

    try:
        body = json.loads(event.get("body", "{}"))
        database_name = body.get("database_name")
        database_engine = body.get("database_engine")
        environment = body.get("environment")

        if not all([database_name, database_engine, environment]):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required parameters"})
            }

        message = {
            "database_name": database_name,
            "database_engine": database_engine,
            "environment": environment
        }

        response = sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=json.dumps(message)
        )

        logger.info("Published to SNS. Message ID: %s", response["MessageId"])

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Request accepted",
                "sns_message_id": response["MessageId"]
            })
        }

    except Exception as e:
        logger.exception("Unhandled exception in lambda_handler")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }



def sqs_handler(event, context):
    """Consumes messages from SQS and creates GitHub PR with Terraform."""
    logger.info("Received event from SQS: %s", json.dumps(event))

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    for record in event["Records"]:
        try:
            body = json.loads(record["body"])
            sns_message = json.loads(body.get("Message", "{}"))

            db_name = sns_message.get("database_name", "exampledb")
            db_engine = sns_message.get("database_engine", "mysql")
            environment = sns_message.get("environment", "dev")
            instance_class = get_instance_class(environment)

            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
            branch_name = f"create-{db_name}-instance-{timestamp}"

            create_branch(repo, branch_name)
            engine_version = get_engine_version(db_engine)

            tf_content = generate_tf_content(db_name, db_engine,engine_version, instance_class, environment)

            repo.create_file(
                path=f"terraform/{db_name}-main.tf",
                message=f"Add Terraform for {db_name}",
                content=tf_content,
                branch=branch_name
            )

            pr = repo.create_pull(
                title=f"Provision RDS for {db_name}",
                body="Auto-created by Lambda!",
                head=branch_name,
                base="main"
            )

            logger.info("Pull Request created: %s", pr.html_url)

        except Exception as e:
            logger.exception("Failed to process message: %s", record)

    logger.info("Finished processing all SQS messages.")
