#!/bin/bash

# IMPORTANT! Run script from root directory of this project

# Define process name
process="$1"

# Get current directory
cur_dir=$(pwd)

# Run all scripts in order
# 1.
source "$cur_dir/scripts/generate_unclean.sh" "$process"
# 2.
source "$cur_dir/scripts/unclean2clean.sh" "$process"
# 3.
source "$cur_dir/scripts/fix_header.sh" "$process"
# 4.
source "$cur_dir/scripts/generate_plots.sh" "$process"
