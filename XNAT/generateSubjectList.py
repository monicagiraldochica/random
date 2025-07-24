#!/usr/bin/env python3
__author__ = "Monica Keith"
__status__ = "Production"

import subprocess
import getpass

# Global variables
# Change address to the corresponding xnat
xnatAddr = "cirxnat1.rcc.mcw.edu:8080/xnat"

# Returns the result of an xnat query in an array
# Each line of the result is one element of the array
def runXNATquery(cmd):
	return subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).communicate()[0].split('\n')[1:-1:1]

# Returns the command for a xnat query
# If things fail, check that the curlBase could change for a different XNAT version or project
# queryType can be: subject_list, experiment_list (requieres sbjID), scan_list (requieres experiment)
def createXNATquery(xnatAddr,project,username,password,queryType,sbjID="",experiment=""):
	curlBase = f"curl --keepalive-time 10 -X GET -u {username}:{password} {xnatAddr}/data/archive/projects/{project}/subjects"
	if queryType=="subject_list":
		return curlBase+"?format=csv"
	if queryType=="experiment_list":
		return curlBase+"/"+sbjID+"/experiments?format=csv"
	if queryType=="scan_list":
		return curlBase+"/"+sbjID+"/experiments/"+experiment+"/scans?format=csv"
	return ""

username = input("Username: ")
password = getpass.getpass(prompt="Password: ")
project = input("Project name: ")
outputName = input("Output file name: ")
outFile = open(outputName,'w')

cmd = createXNATquery(xnatAddr,project,username,password,"subject_list")
for subj in runXNATquery(cmd):
	# Get all the experiments for this subject
	sbjID = subj.split(',')[2]
	cmd = createXNATquery(xnatAddr,project,username,password,"experiment_list",sbjID)

	# For each experiment, find the MPRAGE and mb8 scans
	for exptLine in runXNATquery(cmd):
		exptSplit = exptLine.split(',')
		experiment = exptSplit[5]

		# Get all the scans for this experiment
		cmd = def createXNATquery(xnatAddr,project,username,password,"scan_list",sbjID,experiment)
		scanList = ['NA','NA','NA']

		# For each scan, check to see if it is MPRAGE or MB8 not diagnostic
		for scanLine in runXNATquery(cmd):
			splitScanLine = scanLine.split(',')
			tmpString = splitScanLine[1]+"-"+splitScanLine[2].replace(" ","_").replace(":","_").replace("/","_")

			if "MPRAGE" in scanLine:
				scanList[0] = tmpString
			if "NOT DIAGNOSTIC: MB8 rsfMRI A/P" in scanLine:
				scanList[1] = tmpString
			if "NOT DIAGNOSTIC: MB8 rsfMRI P/A" in scanLine:
				scanList[2] = tmpString

		# Write the line to the file
		outFile.write(sbjID+" "+experiment+" "+exptSplit[3]+" "+scanList[0]+" "+scanList[1]+" "+scanList[2]+"\n")

outFile.close()
