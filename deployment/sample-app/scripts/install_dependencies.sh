#!/bin/bash
yum install -y httpd

# clean up existing index.html to prevent failure in install
sudo rm /var/www/html/index.html || true