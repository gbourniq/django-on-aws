output "arn" {
  description = "Arn of the created ec2 instance"
  value       = aws_instance.myec2.arn
}

output "public_ip" {
  description = "Public IP of the created ec2 instance"
  value       = aws_instance.myec2.public_ip
}