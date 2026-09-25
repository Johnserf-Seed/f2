#!/bin/bash

# Set the character encoding to UTF-8
export LANG=en_US.UTF-8

# Translation sources live next to the compiled catalogs:
# f2/languages/LOCALE/LC_MESSAGES/LOCALE.po is compiled into LOCALE.mo
LOCALES="en_US zh_CN"

# Extract messages (file names only, so moving code around does not touch the .po files)
echo "[INFO] Extracting messages..."
pybabel extract -F babel.cfg --add-location=file -o messages.pot f2 tests
if [ $? -ne 0 ]; then
    echo "Error: Failed to extract messages."
    exit 1
fi

for locale in $LOCALES; do
    po="f2/languages/$locale/LC_MESSAGES/$locale.po"
    mo="f2/languages/$locale/LC_MESSAGES/$locale.mo"

    # Update translations
    echo "[INFO] Updating $po..."
    pybabel update -i messages.pot -o "$po" -l "$locale"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to update $po."
        exit 1
    fi

    # Compile translations
    echo "[INFO] Compiling $mo..."
    pybabel compile -i "$po" -o "$mo" -l "$locale" --statistics
    if [ $? -ne 0 ]; then
        echo "Error: Failed to compile $mo."
        exit 1
    fi
done

echo "[SUCCESS] Done."
