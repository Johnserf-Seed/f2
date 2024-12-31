#!/bin/bash

# Set the character encoding to UTF-8
export LANG=en_US.UTF-8

# Extract messages
echo "[INFO] Extracting messages..."
pybabel extract -F babel.cfg -o messages.pot .
if [ $? -ne 0 ]; then
    echo "Error: Failed to extract messages."
    exit 1
fi

# Update translations
echo "[INFO] Updating translations..."

# Update en_US.po file and redirect logs
echo "[INFO] Updating en_US.po..."
msgmerge -U en_US.po messages.pot > msgmerge_en_US.log 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Failed to update en_US.po. See msgmerge_en_US.log for details."
    exit 1
fi

# Update zh_CN.po file
echo "[INFO] Updating zh_CN.po..."
msgmerge -U zh_CN.po messages.pot > msgmerge_zh_CN.log 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Failed to update zh_CN.po. See msgmerge_zh_CN.log for details."
    exit 1
fi

echo "[SUCCESS] Done."
