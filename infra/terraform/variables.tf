variable "aws_profile" { type = string }
variable "region" { type = string }
variable "vpc_id" { type = string }
variable "subnet_id" { type = string }
variable "ami_id" {
  type        = string
  description = "Approved AL2023 x86_64 AMI in selected region."
}
variable "instance_type" {
  type        = string
  description = "Explicit x86_64 size; review cost before apply."
}
variable "owner" { type = string }
variable "expires_on" {
  type        = string
  description = "Cleanup review date tag, NOT automatic shutdown."
}
variable "expected_account_id" {
  type = string
  validation {
    condition     = can(regex("^[0-9]{12}$", var.expected_account_id))
    error_message = "Supply independently confirmed account ID."
  }
}
variable "report_retention_days" {
  type = number
  validation {
    condition     = var.report_retention_days >= 1 && var.report_retention_days <= 3650 && floor(var.report_retention_days) == var.report_retention_days
    error_message = "Retention must be 1..3650 whole days."
  }
}
variable "egress_rules" {
  type = list(object({
    cidr      = string
    from_port = number
    to_port   = number
  }))
  validation {
    condition = length(var.egress_rules) > 0 && alltrue([
      for r in var.egress_rules :
      can(cidrnetmask(r.cidr)) && r.from_port >= 1 && r.to_port <= 65535 && r.from_port <= r.to_port &&
      floor(r.from_port) == r.from_port && floor(r.to_port) == r.to_port
    ])
    error_message = "Explicit IPv4 destinations and TCP ports required."
  }
}
