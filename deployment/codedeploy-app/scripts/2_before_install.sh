#!/bin/bash
# This script is to install dependencies and any cleanup before copying new files (Install Hook)

set -x

# Install apache
# yum install -y httpd

# clean up existing index.html to prevent failure in install
sudo rm /var/www/html/index.html || true

