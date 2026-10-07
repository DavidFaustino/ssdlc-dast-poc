mock_provider "aws" {
  mock_data "aws_subnet" {
    defaults = { vpc_id = "vpc-12345678" }
  }
  mock_data "aws_ami" {
    defaults = {
      id           = "ami-12345678"
      architecture = "x86_64"
    }
  }
  mock_data "aws_partition" {
    defaults = { partition = "aws" }
  }
}
variables {
  aws_profile           = "offline"
  expected_account_id   = "123456789012"
  region                = "us-east-1"
  vpc_id                = "vpc-12345678"
  subnet_id             = "subnet-12345678"
  ami_id                = "ami-12345678"
  instance_type         = "m6i.xlarge"
  owner                 = "offline-test"
  expires_on            = "2026-10-10"
  report_retention_days = 30
  egress_rules          = [{ cidr = "10.1.0.0/16", from_port = 443, to_port = 443 }]
}
run "private_infrastructure" {
  command = plan
  assert {
    condition     = aws_instance.executor.associate_public_ip_address == false
    error_message = "Executor must have no public IP."
  }
  assert {
    condition     = aws_instance.executor.metadata_options[0].http_tokens == "required"
    error_message = "IMDSv2 is mandatory."
  }
  assert {
    condition     = aws_instance.executor.root_block_device[0].encrypted == true
    error_message = "Disk must be encrypted."
  }
  assert {
    condition     = aws_s3_bucket_public_access_block.reports.block_public_policy && aws_s3_bucket_public_access_block.reports.restrict_public_buckets && aws_s3_bucket_public_access_block.reports.block_public_acls && aws_s3_bucket_public_access_block.reports.ignore_public_acls
    error_message = "Report bucket must block public access."
  }
  assert {
    condition     = aws_s3_bucket.reports.force_destroy == false
    error_message = "Destroy must not silently delete evidence."
  }
}
run "reject_wrong_vpc" {
  command = plan
  variables { vpc_id = "vpc-87654321" }
  expect_failures = [aws_instance.executor]
}
