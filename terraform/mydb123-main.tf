resource "aws_db_instance" "mydb123" {
      identifier              = "mydb123-instance"
      allocated_storage       = 20
      engine                  = "postgres"
      engine_version          = "8.0"
      instance_class          = "db.t3.medium"
      db_name                 = "mydb123"
      username                = "admin"
      password                = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["rds-master-password"]
      skip_final_snapshot     = true
      publicly_accessible     = true

      tags = {
        Name        = "mydb123-instance"
        Environment = "prod"
      }
    }