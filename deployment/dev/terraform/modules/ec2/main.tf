resource "aws_instance" "myec2" {
  ami                    = var.ami
  key_name               = var.key_name
  instance_type          = var.instance_type
  iam_instance_profile   = var.iam_instance_profile
  vpc_security_group_ids = var.vpc_security_group_ids
  tags                   = var.tags
}