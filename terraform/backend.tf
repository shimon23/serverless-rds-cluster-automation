resource "aws_s3_bucket" "terraform_state" {
  bucket = "rds-terraform-state-bucket"
  force_destroy = true

  tags = {
    Name = "Terraform State Bucket"
  }
}

resource "aws_s3_bucket_versioning" "enabled" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}
