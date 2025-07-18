##########################################
# === Terraform Settings ===
##########################################
terraform {
  backend "s3" {
    bucket         = "terraform-state-shimo-automation-2025"
    key            = "terraform.tfstate"
    region         = "eu-central-1"
    encrypt        = true
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"
}

##########################################
# === Get DB Password from Secrets Manager ===
##########################################
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "rds-master-password"
}

##########################################
# === DB Subnet Group ===
##########################################
resource "aws_db_subnet_group" "this" {
  name       = "rds-subnet-group"
  subnet_ids = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id
  ]

  tags = {
    Name = "rds-subnet-group"
  }
}

