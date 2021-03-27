output "public_ips" {
  description = "Public IPs of the provisioned instances"
  value       = join("\n", formatlist("%s:8080", module.myec2instances.*.public_ip))
}

output "workspace_name" {
  description = "Workspace used to create resources"
  value       = terraform.workspace
}
