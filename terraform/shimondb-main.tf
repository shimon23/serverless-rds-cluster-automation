
        resource "aws_db_instance" "shimondb" {
          identifier              = "shimondb-instance"
          allocated_storage       = 20
          engine                  = "mysql"
          engine_version          = "8.0"
          instance_class          = "db.t3.micro"
          db_name                 = "shimondb"
          username                = "admin"
          password                = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["rds-master-password"]
          skip_final_snapshot     = true
          publicly_accessible     = true

          tags = {
            Name        = "shimondb-instance"
            Environment = "dev"
          }
        }
        