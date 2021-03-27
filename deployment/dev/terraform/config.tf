terraform {
  required_version = "~> 0.14"
  required_providers {
    aws   = "~> 2.0"
    null  = "~> 3.1"
    local = "~> 2.1"
  }
  backend "s3" {
    region = "eu-west-2"
    bucket = "terraform-remote-backend-gb"
    key    = "terraform.tfstate"
    # dynamodb_table = "s3-state-lock"
  }
}