variable "database_name" {
  description = "Name of the RDS database"
  type        = string
}

variable "database_engine" {
  description = "Database engine: mysql or postgres"
  type        = string
  default     = "mysql"
}

variable "environment" {
  description = "Environment type: dev or prod"
  type        = string
}
