# Terraform+Ansible Documentation

This README contains instructions on how to set up terraform and ansible to automatically create and configure ec2 instances.

### Pre-requisites

Install the following software and packages on your local machine:
- [terraform cli](https://learn.hashicorp.com/tutorials/terraform/install-cli)
- [terraform-docs](https://github.com/terraform-docs/terraform-docs)
- [tflint](https://github.com/terraform-linters/tflint)
- [pre-commit](https://pre-commit.com)
- [graphviz](https://graphviz.org/download/)
- [ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)


# Terraform documentation

### 1. Create a terraform.tfvars file

```bash
cp terraform.tfvars.template terraform.tfvars
```

The `terraform.tfvars` is used to specify Terraform variables such as the number of ec2 instances to create, and the local machine IP or VPN IP range which should be allowed for inbound ssh connection.

Example of `terraform.tfvars` file:
```
aws_pem_key_name  = "mypersonalkeypair"
environment       = "dev"
instance_count    = 1
provisioning_logs = "~/path/to/tf_provisioning.log"
tag_name          = "Dev deployment"
vpn_ip            = "123.123.123.123/32"
```

### 2. Configure Ansible

Configure ansible variables as per the instructions under `## How to run the playbook`.

### 3. Create and configure infrastructure

The `make apply` command can be run to automatically create and configure the remote servers.

Other useful make commands can be found in the `Makefile`.

### Other useful Terraform commands

Get a human-readable output from a state or plan file.
```
terraform show
```

Extract the value of an output variable from the state file.
```
terraform output
```

Automatically destroy all infrastructure without the user prompt.
```
terraform destroy --auto-approve
```

Commands used for State Management
```
terraform state show aws_instance.myec2
terraform state list
terraform state mv aws_instance.webapp aws_instance.myec2
terraform state pull | jq []
terraform state rm aws_instance.myec2
```

Terraform Workspace commands
```
terraform workspace -h
terraform workspace show
terraform workspace new dev
terraform workspace new prd
terraform workspace list
terraform workspace select dev
```

Test Terraform functions via the console
```
terraform console
```

# Ansible documentation

The Ansible playbooks are used to provision ec2 instances with git repositories and development software packages such as docker, anaconda and poetry.

These playbooks are meant to be run automatically from a terraform module, following the creation of ec2 instances.

------------------------------------------

## Overview

#### Ansible inventories

Ansible inventories are a pattern for defining and grouping managed remote hosts. They are located in `ansible/inventories/`. The addresses of the machines that you want to configure are defined in the hosts file under inventories. You can also specify the ssh keys associated with these hosts in this file as well.

Below is an example of `ansible/inventories/staging/hosts` file which contains a list of remote server public IPs and the ssh key file for Ansible to access the instances.

```
[staging]
18.134.226.25
3.10.227.148

[staging:vars]
ansible_ssh_private_key_file=~/.ssh/terraform_login_key.pem
ansible_user=ec2-user
```

#### Ansible playbooks

Playbooks contain the steps which are set to execute on a particular machine.

This repository contains a `staging.yaml` and `production.yaml` playbooks.


#### Ansible roles

Roles can be found in `ansible/roles/common/` and are ways of automatically loading certain vars_files, tasks, and handlers based on a known file structure. Grouping content by roles also allows easy sharing of roles with other users.

For example, the `docker_deployment.yml` playbook runs the `common` role, which in turn, runs a set of tasks defined in `ansible/roles/common/tasks/main.yaml`.


## How to run the playbook

#### Set environment variables for Ansible

The following environment variables are expected to be set in the `.env` file.
```
export ANSIBLE_HOST_KEY_CHECKING=False
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible_vault_pass
export DOCKER_USER=<dockerhub user>
```

#### Ansible secrets

Variables that we use for sensitive information like passwords are managed by ansible vault. These are stored in an encrypted file, `secrets.yaml`. A password is required to decrypt this file. For automation we can specify this password in a file stored somewhere secure outside of source control.

```bash
touch ~/.ansible_vault_pass
echo "${MY_ANSIBLE_VAULT_PASSPRASE}" > ~/.ansible_vault_pass
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible_vault_pass
ansible-vault encrypt_string '<sensitive-value>' --name '<variable-name>'
```

The encrypted variable can then be stored as an ansible secret in the `secrets.yaml` to be used in ansible roles and playbooks.

So that ansible knows where to look for his file, you should either specify it when running the playbooks with the command line argument `--vault-password-file` or by exporting the `ANSIBLE_VAULT_PASSWORD_FILE` environment variable.

The current playbook expects a `dockerhub_password` secret so that Ansible can log in to dockerhub on the remote servers.


#### Running a playbook

The following command can be run to start the `staging.yaml` playbook. 
```bash
cd ansible
source .env
ansible-playbook -i inventories staging.yaml -v --timeout 60
```
