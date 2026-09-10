#!/bin/bash

ORIGINAL_NAME="dlt"
NEW_NAME="data_load_tool"

# Rename the package directory
if [ -d "$ORIGINAL_NAME" ]; then
    mv "$ORIGINAL_NAME" "$NEW_NAME"
    echo "Renamed folder $ORIGINAL_NAME → $NEW_NAME"
else
    echo "Folder $ORIGINAL_NAME not found!"
    exit 1
fi

# Update all dlt mentions besides words with "dlt" as substring surounded by "-" or "_"
# FORK.md and this script belong to the fork, not to upstream. Both hold "dlt" as
# prose or as data, so a rename inside them corrupts them.
find . -type f ! -path "./.git/*" ! -path "./rename_dlt.sh" ! -path "./FORK.md" \
    -exec perl -i -pe "s/(?<![-_])\b$ORIGINAL_NAME\b(?![-_])/$NEW_NAME/g" {} +
echo "Updated all dlt mentions in files"

# Rename ".dlt" hidden folders
# -depth moves a folder only after find read its contents, so find does not then
# try to descend into the old path and report it as missing.
find . -depth -type d -name ".$ORIGINAL_NAME" -execdir mv {} ".$NEW_NAME" \;
echo "Renamed all .$ORIGINAL_NAME folders"

echo "Done!⚡️ Package renamed"