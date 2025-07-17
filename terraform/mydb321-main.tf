resource "aws_db_instance" "mydb321" {
      identifier              = "mydb321-instance"
      allocated_storage       = 20
      engine                  = "postgres"
      engine_version          = "8.0"
      instance_class          = "db.t3.medium"
      db_name                 = "mydb321"
      username                = "admin"
      password                = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["rds-master-password"]
      skip_final_snapshot     = true
      publicly_accessible     = true

      tags = {
        Name        = "mydb321-instance"
        Environment = "prod"
      }
    }