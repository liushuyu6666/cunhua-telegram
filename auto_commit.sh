#!/bin/bash
# Usage: ./auto_commit.sh "your commit message"

# Run pre-commit hooks (isort, black, etc.) on all files
pre-commit run --all-files

# Add any changes made by hooks
git add .

# Commit with the provided message
if [ -z "$1" ]; then
  echo "Please provide a commit message."
  exit 1
fi

git commit -m "$1"
