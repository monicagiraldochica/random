#!/usr/bin/env python3
__author__ = "Monica Keith"
__status__ = "Production"
__purpose__ = "Fiz the ImageMagick color table in  my bash tutorial"

fin = open("colorlist.txt",'r'a
lines = fin.readLines()[2:]
fin.close()

for line in lines:
	print(line)
