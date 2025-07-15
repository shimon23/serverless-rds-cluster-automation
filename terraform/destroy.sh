#!/bin/bash

echo "Starting Terraform Destroy..."

terraform destroy -var="database_name=testdb" -var="database_engine=mysql" -var="environment=dev" -auto-approve

echo "All resources destroyed!"
