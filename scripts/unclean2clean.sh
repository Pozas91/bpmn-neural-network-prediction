#!/bin/bash
# shellcheck disable=SC2045

for path in $(ls -1 outputs/"$1"/*/*/*.unclean); do
  # Get file name (with extension)
  file=$(basename -- "$path")
  # Get dir name
  dir=$(dirname -- "$path")
  # Get file name (no extension)
  name="${file%.*}"
  # Execute python script
  poetry run python maude/interaction/sandbox/unclean2clean.py <"$path" >"$dir/$name.clean"
done
