#!/bin/bash

#echo "# User exists and is enabled"
#python3 create_acct.py --user=aahaider --pi=jbinder

#echo "# New user, PI doesnt have an account"
#python3 create_acct.py --user=mmkeith --pi=jbinderr

#echo "# New user, PI is not a PI"
#python3 create_acct.py --user=mmkeith --pi=mkeith

#echo "# User is disabled and was not a PI"
#python3 create_acct.py --user=adirck --pi=jbinder

#echo "# User is disabled and was a pi"
#python3 create_acct.py --user=deyoe --pi=jbinder

echo "# User is new, correct PI, user is not a PI. Add to Neurology Desktops & squiggles"
python3 create_acct.py --user=cnaranjo --pi=jbinder --first=Carolina --last=Naranjo --email=cnaranjo@mcw.edu --ndesktops --nsquiggles

##echo "# User is new, correct PI, user is not a PI"
##python3 create_acct.py --user=mchica --pi=jbinder --first=Myriam --last=Chica --email=mchica@mcw.edu

##echo "# User is new, correct PI, user is a PI"
##python3 create_acct.py --user=ngiraldo --pi=ngiraldo --first=Natalia --last=Giraldo --email=ngiraldo@mcw.edu
