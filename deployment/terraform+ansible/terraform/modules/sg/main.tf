resource "aws_security_group" "dynamic_sg" {
  name        = "dynamic-sg"
  description = "Inbound http/s and all outbound ports allowed"
  dynamic "ingress" {
    for_each = var.sg_ports
    iterator = port
    content {
      from_port   = port.value
      to_port     = port.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = var.tags
}

resource "aws_security_group" "ssh_sg" {
  name        = "ssh-sg"
  description = "Inbound SSH allowed"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.vpn_ip]
  }
  tags = var.tags
}