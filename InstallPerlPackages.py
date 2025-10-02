#!/usr/bin/env python3
__author__ = "Monica Keith"
__status__ = "Production"
__purpose__ = "Install Perl packages"

import os
import pandas as pd

os.chdir("/group/rccadmin/work/mkeith/perl")
v_new = "5.42.0"
v_old = "5.26.1"

# Put the list of modules from the new version in an ordered DF
df_new = pd.read_csv(f"{v_new}.txt", sep="\t", header=None)
print(df_new)

# Put the list of modules from the old version in an ordered DF

# Get the list of missing packages

# Create files to store the modules that successfully & unsuccessfully installed
#fout1 = open("sucess.txt",'w')
#fout1.close()
#fout2 = open("fail.txt",'w')
#fout2.close()

# Install missing modules