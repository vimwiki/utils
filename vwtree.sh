#!/bin/bash
# Create a linkified vimwiki file of unchecked todo items and a tree of the specified directory and
#   subdirectories. For the links to make sense, save the output of this script into a file located
#   in this base directory.
# This script requires `tree` and `perl` to be installed.

# Define usage.
usage() {
  cat <<EOF
Usage: $0 [-t|-c|-h] [DIRECTORY]
  -t          only print todo items
  -c          only print table of contents
  -h          display this help text and exit
  DIRECTORY   specify the base directory (default is current directory)
EOF
  exit 1
}

# Set default options, to print both todo and contents.
just_todo='false'
just_contents='false'

# Parse options.
while getopts 'tch' opt; do
  case "${opt}" in
    t) just_todo='true' ;;
    c) just_contents='true' ;;
    *) usage; exit 1 ;;
  esac
done
shift $((OPTIND-1))

# You can't "just print" both.
if $just_todo && $just_contents; then
  echo 'Error: incompatible options.'
  usage
fi

# If there is no argument supplied, this will stay in the current directory.
cd "$1"

# Print todo section.
if ! $just_contents; then
  # Print todo header.
  echo '= Todo items ='

  # If a todo item is found, print the relevant information.
  print_matches() {
    todo_pattern='^\s*[*-] \[ \]'
    if grep -q "$todo_pattern" "$1"; then
      matches="$(grep "$todo_pattern" "$1")"
      # Format page_name for vimwiki syntax, i.e. no leading `./` or trailing `.wiki`
      page_name="$(echo $1 | sed -r 's/^.\/(.*).wiki/\1/')"
      # Escape literal slashes, otherwise the next sed will choke.
      escaped_page_name="$(echo "$page_name" | sed 's,/,\\/,g')"
      printf %s "$matches" | sed "s/^/* [[${escaped_page_name}]]: /"
      echo
    fi
  }

  # Search for todo items.
  export -f print_matches
  find . -name '*.wiki' -exec bash -c 'print_matches "$0"' {} \;
  echo
fi

# Print contents section.
if ! $just_todo; then
  # Print contents header.
  echo '= Table of contents ='

  while IFS='' read -r line; do
    # Use perl regex in case there are files with ── in their name.
    filename="$(<<<"$line" perl -pe 's/.*?── (.*)/\1/' )"
    treetrunk="$(<<<"$line" perl -pe 's/(.*?── ).*/\1/')"

    # Calculate depth of current file, where 1 is current directory.
    depth=$(( $(<<<"$treetrunk" wc -m ) / 4 ))

    # Work out path.
    path_array[$depth]="$filename"
    path_formatted="$(printf "/%s" "${path_array[@]:1:$depth}")"
    path_formatted="${path_formatted:1}"

    # Print out line.
    echo -n "$treetrunk"
    if $(<<<"$filename" grep -q '.wiki$'); then
      echo "[[${path_formatted%.wiki}|${filename%.wiki}]]"
    else
      echo "$filename"
    fi
  done <<< "$(tree | head -n -2 | tail -n +2)"
fi
