[staging]
%{ for ip in public_ips ~}
${ip}
%{ endfor ~}

[staging:vars]
ansible_ssh_private_key_file=~/.ssh/terraform_login_key.pem
ansible_user=ec2-user