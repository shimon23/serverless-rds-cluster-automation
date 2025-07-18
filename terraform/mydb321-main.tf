resource "aws_db_instance" "mydb321" {
      identifier              = "mydb321-instance"
      allocated_storage       = 20
      engine                  = "postgres"
      engine_version          = "15.10"
      instance_class          = "db.t3.medium"
      db_name                 = "mydb321"
      username                = "rdsuser"
      password                = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["rds-master-password"]
      skip_final_snapshot     = true
      publicly_accessible     = true

      tags = {
        Name        = "mydb321-instance"
        Environment = "prod"
      }
    }