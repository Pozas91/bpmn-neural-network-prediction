#!/bin/bash
# shellcheck disable=SC2045

# For each file
for path in $(ls -1 maude/examples/"$1"/runs/*.maude); do

  if [[ "$path" == *predictive-ml-usage-2* ]]; then
    # Avoid work with experimental predictive ml
    continue
  fi

  # Get file name (with extension)
  file=$(basename -- "$path")
  # Get file name (no extension)
  name="${file%.*}"
  # Prepare new dir name
  new_dir="${name//bpmn-run-$1-/}"

  # Time between checks
  for tbc in {1..10}; do
    # Replace always tbc variable
    sed -i -E "s/(TIME-BETWEEN-CHECKS = )([0-9]*)/\1$tbc/g" "$path"

    if [[ "$path" == *predictive* ]]; then
      # Replace PS for predictive files
      for ps in {1..10}; do
        # Replace information
        sed -i -E "s/(PREDICTION-SIZE = )([0-9]*)/\1$ps/g" "$path"
        sed -i -E "s/(PREDICTION-TIME = )([0-9]*)/\1$ps/g" "$path"

        # Define output dir
        out_dir="outputs/$1/$new_dir/$tbc-$ps/"

        # Make sure has been created
        mkdir -p "$out_dir"

        # Execute maude to dump information
        ~/maude/maude.linux64 "$path" >"$out_dir/file.unclean"
      done
    else
      # Replace CI for all files except predictive
      for ci in {1..10}; do
        # Replace information
        sed -i -E "s/(CHECK-INTERVAL = )([0-9]*)/\1$ci/g" "$path"

        # Define output dir
        out_dir="outputs/$1/$new_dir/$tbc-$ci/"

        # Make sure has been created
        mkdir -p "$out_dir"

        # Execute maude to dump information
        ~/maude/maude.linux64 "$path" >"$out_dir/file.unclean"
      done
    fi

  done
done
