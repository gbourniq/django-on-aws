output "dynamic_sg_id" {
  description = "Id of the created security group with dynamic ports"
  value       = aws_security_group.dynamic_sg.id
}

output "ssh_sg_id" {
  description = "Id of the created security group for ssh access"
  value       = var.vpn_ip != "" ? aws_security_group.ssh_sg.id : null
}