##########################################
# === Terraform Settings ===
##########################################
terraform {
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
  name       = "${var.database_name}-subnet-group"
  subnet_ids = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id
  ]

  tags = {
    Name = "${var.database_name}-subnet-group"
  }
}

##########################################
# === Standard RDS Instance ===
##########################################
resource "aws_db_instance" "this" {
  identifier              = "${var.database_name}-instance"
  allocated_storage       = 20
  engine                  = var.database_engine
  engine_version          = "8.0"
  instance_class          = "db.t3.micro"  # ✅ Free Tier eligible
  db_name                 = var.database_name  # ✅ Correct!
  username                = "admin"
  password                = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["rds-master-password"]
  db_subnet_group_name    = aws_db_subnet_group.this.name
  skip_final_snapshot     = true
  publicly_accessible     = true

  tags = {
    Name        = "${var.database_name}-instance"
    Environment = var.environment
  }
}
