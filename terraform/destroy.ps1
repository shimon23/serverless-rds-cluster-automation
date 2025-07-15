Write-Host "🚀 Starting Terraform Destroy..."

terraform destroy -var="database_name=testdb" -var="database_engine=mysql" -var="environment=dev" -auto-approve

Write-Host "✅ All resources destroyed!"
