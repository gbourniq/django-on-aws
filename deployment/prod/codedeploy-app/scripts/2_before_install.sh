#!/bin/bash
set -e
# Preinstall tasks, such as decrypting files and creating a backup of the current version
# or any cleanup tasks before copying new files to the host (Install Hook)

echo "Clean up existing files"
sudo rm -rf /home/ec2-user/mounts
