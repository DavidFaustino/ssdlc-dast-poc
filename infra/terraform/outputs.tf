output "executor_instance_id" { value = aws_instance.executor.id }
output "reports_bucket" { value = aws_s3_bucket.reports.id }
output "executor_private_ip" { value = aws_instance.executor.private_ip }
output "session_command" {
  value = "aws ssm start-session --target ${aws_instance.executor.id} --profile ${var.aws_profile} --region ${var.region}"
}
