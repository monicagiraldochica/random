#!/bin/bash
# Author: Monica Keith
# Created: 2025-09-26
# Description: Find the subfolders that were accessed the longest ago inside a folder

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

# Enable dotglob to include hidden files/folders in globbing
shopt -s dotglob

# Array to store results
declare -a oldest_dirs

# Loop over all top-level folders, including hidden
for dir in "${searchdir}/*"; do
	# Skip "." and ".."
	if [ "$dir" = "$searchdir/." ] || [ "$dir" = "$searchdir/.." ]; then
		continue
	fi

	echo -e "${dir}\n"

	# Find the oldest access time among files inside the directory
	#newest_access=$(find "$dir" -type f -printf '%A@ %p\n' 2>/dev/null | sort -n | head -n1 | awk '{print $1}')

	# If the directory has no files, fallback to directory's own access time
	#if [ -z "$newest_access" ]; then
        #	newest_access=$(stat -c %X "$dir")
    	#fi

	# Store access time and directory path in the array
    	#oldest_dirs+=("$newest_access $dir")
done

# Disable dotglob to restore default behavior
shopt -u dotglob

# Sort by access time (oldest first) and take only the top $nlines
#for entry in $(printf "%s\n" "${oldest_dirs[@]}" | sort -n | head -n "$nlines"); do
    	#echo $entry
	#ts=$(echo "$entry" | awk '{print $1}')
    	#dir=$(echo "$entry" | awk '{print $2}')
    	# Print human-readable date and directory
    	#echo -e "$(date -d @"$ts" '+%Y-%m-%d %H:%M:%S')\t$dir"
#done
