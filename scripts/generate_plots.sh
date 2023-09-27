#!/bin/bash
# shellcheck disable=SC2045

for path in $(ls -1 outputs/"$1"/*/*/*.clean); do
  # Get current directory
  cur_dir=$(pwd)
  # Get file name (with extension)
  file=$(basename -- "$path")
  # Get dir name
  dir=$(dirname -- "$path")
  # Go to $dir
  cd "$dir" || exit
  # Execute python script
  poetry run python "$cur_dir/maude/interaction/sandbox/clean2plot.py" <"$file"
  # Back to $cur_dir
  cd "$cur_dir" || exit
done
