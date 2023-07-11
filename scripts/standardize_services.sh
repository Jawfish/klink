#!/bin/bash

# This file is for standardizing service configuration and development environments.
#
# Available flags:
# --overwrite:   Automatically overwrite existing files without asking.
# --no-overwrite: Automatically skip existing files without asking.
#
# Without any flags, the script will ask for confirmation before overwriting each existing config file.

# Define the configuration files
default_config_file="log_config.example.json"
config_file="log_config.json"

# Define the service directories
service_dirs=("../frontend_service" "../gateway_service" "../user_service" "../post_service" "../tag_service")

# Set the overwrite mode to 'ask' initially
overwrite="ask"

# Check for --overwrite and --no-overwrite flags
if [[ $1 == "--overwrite" ]]; then
  overwrite="yes"
elif [[ $1 == "--no-overwrite" ]]; then
  overwrite="no"
fi

# Loop through each service directory
for dir in "${service_dirs[@]}"; do
  # Determine which file to copy
  file_to_copy=$config_file
  if [[ ! -e $config_file ]]; then
    # If the config file doesn't exist, print a warning and use the default config file
    echo "WARNING: $config_file not found, using $default_config_file instead"
    file_to_copy=$default_config_file
  fi

  # Check if the file already exists in the service directory
  if [[ -e $dir/$config_file ]]; then
    if [[ $overwrite == "ask" ]]; then
      # If no flags were passed, ask for confirmation before overwriting
      echo "$dir/$config_file already exists. Overwrite? (y/n)"
      read -n 1 -r
      echo
      if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping $dir/$config_file"
        continue
      fi
    elif [[ $overwrite == "no" ]]; then
      # If the --no-overwrite flag was passed, skip this file
      echo "Skipping $dir/$config_file due to --no-overwrite flag."
      continue
    else
      # If the --overwrite flag was passed, print a message and proceed with overwriting
      echo "Overwriting $dir/$config_file due to --overwrite flag."
    fi
  fi

  # Copy the file to the service directory and print a message
  echo "Copying $file_to_copy to $dir/$config_file"
  cp $file_to_copy $dir/$config_file
done
