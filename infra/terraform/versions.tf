terraform {
  required_version = ">= 1.9.0, < 2.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.15.0"
    }
  }
}
provider "aws" {
  profile             = var.aws_profile
  region              = var.region
  allowed_account_ids = [var.expected_account_id]
  default_tags {
    tags = {
      Project   = "ssdlc-dast-poc"
      ManagedBy = "terraform"
      Owner     = var.owner
      ExpiresOn = var.expires_on
    }
  }
}
