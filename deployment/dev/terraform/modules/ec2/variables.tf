variable "ami" {
  type        = string
  description = "The id of the machine image (AMI) to use for the server."
  default     = null

  validation {
    condition     = can(regex("^ami-", var.ami))
    error_message = "The image_id value must be a valid AMI id, starting with \"ami-\"."
  }
}

variable "instance_type" {
  description = "The type of instance to start."
  type        = string
  default     = "t2.micro"
  validation {
    condition     = can(regex("^t2.micro$", var.instance_type))
    error_message = "The instance_type value must match the allowed pattern(s)."
  }
}

variable "key_name" {
  description = "The key name to use for the instance."
  type        = string
  default     = ""
}

variable "vpc_security_group_ids" {
  description = "A list of security group IDs to associate with."
  type        = list(string)
  default     = null
}

variable "tags" {
  description = "A mapping of tags to assign to the resource."
  type        = map(string)
  default     = {}
}

variable "iam_instance_profile" {
  description = "The IAM Instance Profile to launch the instance with. Specified as the name of the Instance Profile."
  type        = string
  default     = ""
}