#!/bin/bash
# shellcheck disable=SC2045

for path in $(ls -1 outputs/"$1"/*/*/*.clean); do
  # Get file name (with extension)
  file=$(basename -- "$path")
  # Get file name (no extension)
  name="${file%.*}"
  # Replace first line by $name variable
  sed -i "1 s/.*/$name/" "$path"
done
