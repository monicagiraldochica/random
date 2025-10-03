#!/usr/bin/env python3
__author__ = "Monica Keith"
__status__ = "Production"
__purpose__ = "Install Perl packages"

import os
import subprocess

def check_module(mdl):
    cmd = ['perl', f"-M{mdl}", '-e', 'print "Installed\n"']

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout.strip()  # remove trailing newlines
        return output == "Installed"
    except subprocess.CalledProcessError as e:
        if "Can't locate" in e.stderr:
            return False
        raise

os.chdir("/group/rccadmin/work/mkeith/perl")
v_new = "5.42.0"
v_old = "5.26.1"

# Put the list of modules from the new version in an ordered DF
dic_new = {}
with open(f"{v_new}.txt", "r") as f:
    for line in f:
        line = line.strip().split("\t")
        dic_new[line[0]] = line[1]

# Put the list of modules from the old version in an ordered DF
dic_old = {}
with open(f"{v_old}.txt", "r") as f:
    for line in f:
        line = line.strip().split("\t")
        dic_old[line[0]] = line[1]

# Get the list of missing packages
missing_keys = set(dic_old.keys()) - set(dic_new.keys())

# Install missing modules
for mdl in missing_keys:
    try:
        if check_module(mdl):
            print(f"{mdl} is already installed")
        else:
            print(f"Installing {mdl}")
            os.system(f"cpan -T {mdl}")

    except subprocess.CalledProcessError as exc:
        print("An unexpected error occurred:", exc)
        break

# Check install
fout1 = open("sucess.txt",'w')
fout2 = open("fail.txt",'w')

for mdl in missing_keys:
    try:
        if check_module(mdl):
            fout1.write(f"{mdl}\n")
        else:
            fout2.write(f"{mdl}\n")

    except subprocess.CalledProcessError as exc:
        print("An unexpected error occurred:", exc)
        break

fout2.close()
fout1.close()
