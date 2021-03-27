variable "sg_ports" {
  type        = list(number)
  description = "list of ingress ports"
  default     = [80, 443]
}

variable "vpn_ip" {
  type        = string
  description = "your IP address for ssh access"
  default     = ""
}

variable "tags" {
  description = "A mapping of tags to assign to the resource."
  type        = map(string)
  default     = {}
}