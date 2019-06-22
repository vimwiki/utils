#!/bin/bash
# Create a linkified vimwiki tree of the specified directory and subdirectories.
# It takes one argument: the base directory of the vimwiki.
# For the links to make sense, save the output of this script into a file located in this base directory.
# This script requires `tree` to be installed.

# Print header
echo '= Table of contents ='
echo

cd "$1"
while IFS='' read -r line; do
  # Assuming there are no files with ── in their name.
  filename="$(<<<"$line" sed -r 's/.*── (.*)/\1/' )"
  treetrunk="$(<<<"$line" sed -r 's/(.*── ).*/\1/')"

  # Calculate depth of current file, where 1 is current directory.
  depth=$(( $(<<<"$treetrunk" wc -m ) / 4 ))

  # Work out path
  path_array[$depth]="$filename"
  path_formatted="$(printf "/%s" "${path_array[@]:1:$depth}")"
  path_formatted="${path_formatted:1}"

  # Print out line
  echo -n "$treetrunk"
  if $(<<<"$filename" grep -q '.wiki$'); then
    echo "[[${path_formatted%.wiki}|${filename%.wiki}]]"
  else
    echo "$filename"
  fi
done <<< "$(tree | head -n -2 | tail -n +2)"
