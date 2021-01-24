#!/bin/bash

set -x

# This script is to install dependencies and any cleanup logic
# before copying new files, at the Install Hook

# Remove the index.html created from cfn-init
sudo rm /var/www/html/index.html || true

