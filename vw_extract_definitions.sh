#!/bin/sh

###########################
# vw_extract_definitions.sh
###########################
#
# Finds all terms/definitions in a vimwiki and saves them in a tsv (to be added
# to anki)
#
# You can add a DECK definition to your vimwiki files above normal definitions
# to separate your terms into different output files. All following definitions
# will be placed in that category until a new DECK is declared or a new file
# starts. Failing to declare DECK will default definitions to a default file.
#
# Example:
#   == My Document ==
#   DECK::Animals
#   Fox::A small red furry creature
#   Hedgehogs::Spiky thing, good for throwing at enemies
#   DECK::Software
#   Fox::Mascot of a popular browser
#
###########################


usage="
vw_extract_definitions.sh source dest\n
Where:\n
source -- is the name of a directory containing vimwiki text files\n
dest -- is the name of the directory to be used for output files\n
"
 
if [ "$#" -ne 2 ]; then 
    echo $usage
    exit
fi 

loc=$1
dest=$2
default='wiki-cards'

now=$(date +"%Y-%m-%d")

mkdir -p "$dest"

tail -n +1 "$loc"/* |
sed 's/^==>.*/DECK::'$default'/' | 
awk '
BEGIN {
    FS = "::";
    VALUE = 0;
    WORD = ""
    DEF = ""
    DECK = "";
}
{
    if (NF<=1 && VALUE == 1) {
        if(WORD == "DECK") {
            DECK = DEF;
        } else {
            printf("%s\t%s\n",WORD,DEF) >> ("'$dest'/" DECK "-'$now'.tsv");
        }
        VALUE = 0;
    } else if (NF==2) {
        # If new definition
        if ($1 != ""){
          # Clean up old definition
          if(VALUE == 1){
            if(WORD == "DECK") {
                DECK = DEF;
            } else {
                printf("%s\t%s\n",WORD,DEF) >> ("'$dest'/" DECK "-'$now'.tsv");
            }
            VALUE = 0;
          }
          # New Definition
          WORD = $1;
          DEF = $2;
        } else if(VALUE == 1){
          DEF=DEF $2;
        }
        VALUE = 1;
    }
}
END{}
'
