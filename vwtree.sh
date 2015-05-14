#!/usr/bin/env bash
# Create a linkified vimwiki tree of the specified directory and subdirectories.
# It takes one optional argument: the base directory of the vimwiki.
# Otherwise, the current directory is assumed to be the base directory.
# For the links to make sense, save the output of this script into a file located in this base directory.
# This script requires `tree` and `perl` to be installed.

cd "$1" # If there is no argument supplied, this will not change the current directory.

# Print header
echo '= Table of contents ='

while IFS='' read -r line; do
  # Use perl regex in case there are files with ── in their name.
  filename="$(<<<"$line" perl -pe 's/.*?── (.*)/\1/' )"
  treetrunk="$(<<<"$line" perl -pe 's/(.*?── ).*/\1/')"

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
