#!/bin/bash

# List of Python scripts to execute
scripts=(
  "extract.py"
  "extract_fred.py"
  "extract_filings.py"
  "macro_model.py"
)

# Loop through the scripts and execute them
for script in "${scripts[@]}"; do
  echo "Running $script..."
  python "$script"
  
  # Check if the script ran successfully
  if [ $? -ne 0 ]; then
    echo "Error: $script failed to execute."
    exit 1
  fi
done

echo "All scripts executed successfully!"