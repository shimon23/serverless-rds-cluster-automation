resource "aws_db_instance" "testci5" {
      identifier              = "testci5-instance"
      allocated_storage       = 20
      engine                  = "postgres"
      engine_version          = "15.10"
      instance_class          = "db.t3.medium"
      db_name                 = "testci5"
      username                = "rdsuser"
      password                = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["rds-master-password"]
      skip_final_snapshot     = true
      publicly_accessible     = true

      tags = {
        Name        = "testci5-instance"
        Environment = "prod"
      }
    }