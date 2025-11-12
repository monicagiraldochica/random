#!/bin/bash
# Author: Monica Keith
# Created: 2025-09-26
# Description: Find the subfolders that occupy the most space inside a folder

## Global variables
nlines=0
searchdir=""

## Functions
printhelp(){
	echo -e "Mandatory flags:\n" \
		"\t-n N\t: Print N lines max\n" \
		"\t-f folder\t: Search folder\n"

	exit
}

parse_args() {
	while getopts ":hn:f:" opt; do
		case $opt in
			h) printhelp;;
			n) nlines=$OPTARG;;
			f) 
				searchdir=$OPTARG
				# Remove trailing backslash if present
				if [[ "${searchdir: -1}" == '/' ]]; then
					searchdir="${searchdir::-1}"
				fi
				;;
			\?) echo "Invalid option: -$OPTARG" >&2; exit 1;;
			:) echo "Option -$OPTARG requires an argument." >&2; exit 1;;
		esac
	done
}

## Main code
parse_args "$@"

#find "${searchdir}" -mindepth 1 -maxdepth 1 \( -name ".*" -o -name "*" \) -exec sh -c '
#  for path do
#	echo $path
#    size=$(du -sh "$path" 2>/dev/null | awk "{print \$1}")
#    owner=$(stat -c "%U" "$path")
#    echo -e "$size\t$owner\t$path"
#  done
#' sh {} + | sort -h | tail -n "$nlines"

for path in "$searchdir"/*; do
	size=$(du -sh "$path" 2>/dev/null | awk "{print \$1}")
	owner=$(stat -c "%U" "$path")
    echo -e "$size\t$owner\t$path"
done | sort -hr