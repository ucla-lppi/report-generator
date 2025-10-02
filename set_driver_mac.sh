#!/bin/bash

# Define additional paths
PYTHON_PATH="$HOME/python"
WKHTML_PATH="/usr/local/bin" # adjust if wkhtmltopdf is elsewhere

EXPORT_CMD="export PATH=\"$PYTHON_PATH:$WKHTML_PATH:\$PATH\""

# Detect shell and select appropriate config file
if [ -n "$ZSH_VERSION" ] || [ "$(basename "$SHELL")" = "zsh" ]; then
  CONFIG_FILE="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ] || [ "$(basename "$SHELL")" = "bash" ]; then
  CONFIG_FILE="$HOME/.bash_profile"
else
  echo "Unsupported shell. Please add this line manually to your shell profile:"
  echo "$EXPORT_CMD"
  exit 1
fi

# Add PATH export only if not already present
if ! grep -Fxq "$EXPORT_CMD" "$CONFIG_FILE"; then
  echo "$EXPORT_CMD" >> "$CONFIG_FILE"
  echo "Added PATH update to $CONFIG_FILE."
else
  echo "PATH already updated in $CONFIG_FILE."
fi

# Immediately update current session
eval "$EXPORT_CMD"
echo "PATH updated for current shell session."
