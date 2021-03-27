# General
variable "provisioning_logs" {
  description = "Local path to the provisioning logs file."
  type        = string
  default     = null
}

variable "tag_name" {
  description = "Name to tag aws resources with."
  type        = string
  default     = null
}

# EC2
variable "instance_count" {
  description = "Number of instances to launch."
  type        = number
  default     = 1
}

variable "environment" {
  type        = string
  description = "placeholder"
  default     = "dev"

  validation {
    condition     = can(regex("^(dev|prod)$", var.environment))
    error_message = "The environment must be set to dev or prod to be valid."
  }
}

variable "instance_type" {
  type        = map(string)
  description = "A map to compute the instance type to launch based on the environment"
  default = {
    dev  = "t2.micro"
    prod = "t2.large"
  }
}

variable "aws_pem_key_name" {
  description = "The key name to use for the instance."
  type        = string
  default     = ""
}

variable "iam_instance_profile" {
  description = "The IAM Instance Profile to launch the instance with. Specified as the name of the Instance Profile."
  type        = string
  default     = ""
}

# Security Groups
variable "sg_ports" {
  type        = list(number)
  description = "list of ingress ports"
  default     = [80, 443, 8080]
}

variable "vpn_ip" {
  type        = string
  description = "your IP address for ssh access"
  default     = null
}

