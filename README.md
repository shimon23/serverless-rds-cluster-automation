Serverless RDS Cluster Provisioning
Provision on-demand RDS databases (PostgreSQL / MySQL) through a secure serverless API using AWS Lambda, SAM, Terraform, and GitHub automation.

🔁 Full Flow Overview
[Client]
   ⬇ POST /provision-rds (JSON + API Key)
[API Gateway]  ← created using AWS SAM
   ⬇
[Lambda Function #1 (API handler)] ← defined in SAM
   ⬇ publishes to
[SNS Topic] ← defined in SAM
   ⬇
[SQS Queue] ← defined in SAM
   ⬇ triggers
[Lambda Function #2 (Queue consumer)] ← defined in SAM
   ⬇
[GitHub] ← creates PR with Terraform .tf file
   ⬇
[CircleCI] ← runs Terraform apply
   ⬇
[RDS Instance] ← created by Terraform

All API Gateway, Lambda, SNS, and SQS resources are defined and deployed using AWS SAM (template.yaml).

Architecture Components
Component
Provisioned Using
Description
API Gateway
AWS SAM
Public REST endpoint with API Key auth
Lambda Functions
AWS SAM
One for API handling, one for queue consumption
SNS & SQS
AWS SAM
Decouples API requests from provisioning logic
GitHub PR Logic
Python Lambda
Creates .tf file in PR to provision DB
Terraform
IaC
Manages actual RDS resources
S3 Backend
Terraform
Shared state for consistent provisioning
CircleCI
CI/CD
Triggers provisioning on PR merge to main
Secrets Manager
AWS
Stores DB credentials securely
Route53 Domain
AWS
Custom domain for the API Gateway


Deployment Instructions
1. Deploy the Serverless Stack (SAM)
cd sam
sam build
sam deploy --guided

This deploys all serverless infrastructure: API Gateway, Lambdas, SNS, SQS.

How to Use the API
POST https://your-api-url/prod/provision-rds
x-api-key: YOUR_API_KEY
Content-Type: application/json

{
  "database_name": "mydb123",
  "database_engine": "mysql",
  "environment": "dev"
}

This request will:
Send message to SNS → SQS → Lambda


Lambda creates a .tf file and PR in GitHub


On PR merge to main, Terraform is applied and RDS instance is created



📄 Repository Structure
.
├── .circleci/               # CircleCI pipeline
├── lambda/                  # Python handlers (API and SQS)
├── sam/                     # AWS SAM templates
│   └── template.yaml
├── terraform/               # Terraform files (dynamically added)
└── README.md

Features
AWS SAM for serverless provisioning


Full IaC with Terraform + S3 backend


GitHub PR-based provisioning workflow


CircleCI automation on merge


Secrets via AWS Secrets Manager


Custom Domain via Route 53


API Key authentication for API Gateway


Bonus: Auto cleanup support (TTL tagging)



🛠 Prerequisites
AWS CLI + credentials


GitHub repo with Terraform and Lambda files


CircleCI connected to the GitHub repo


AWS SAM CLI installed
