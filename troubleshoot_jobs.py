#!/usr/bin/env python3.10
import subprocess
import pandas as pd
import re

# Only works for running, queued or recently finished jobs
def get_jobInfo_scontrol(job_id):
    """
    Get selected job information from scontrol for a given job ID.
    Returns a pandas DataFrame with columns ['Field', 'Value'].
    Returns an empty DataFrame if job is not found in Slurm memory.
    """
    try:
        # Run scontrol command
        result = subprocess.run(["scontrol", "show", "job", str(job_id)], capture_output=True, text=True, check=True)

    except subprocess.CalledProcessError:
        # Job not found or command failed
        return pd.DataFrame()

    output = result.stdout.strip()
    if not output or "JobId" not in output:
        # Job not in memory or invalid
        return pd.DataFrame()

    # Flatten multiline scontrol output
    output = re.sub(r'\s+', ' ', output)

    # Parse key=value pairs
    data = dict(re.findall(r'(\S+?)=(\S+)', output))

    # Extract only requested fields
    fields = [ "UserId", "JobState", "Reason", "RunTime", "TimeLimit", "SubmitTime", "StartTime", "EndTime", "Partition", "NodeList", "ReqTRES", "AllocTRES", "Command", "StdErr", "StdOut", "WorkDir" ]
    info = [(field, data.get(field, "")) for field in fields]

    # Return as DataFrame
    return pd.DataFrame(info, columns=["Field", "Value"])

# Better to use for failed or completed jobs
def get_jobInfo_sacct(job_id):
    """
    Get selected job information from sacct for a given job ID.
    Returns a pandas DataFrame with columns ['Field', 'Value'].
    Returns an empty DataFrame if no sacct data exists yet.
    """
    fields = [ "User", "State", "ExitCode", "ReqMem", "AveRSS", "MaxRSS" ]
    #fields = [ "User", "State", "ExitCode", "DerivedExitCode", "Elapsed", "Timelimit", "Submit", "Start", "End", "Partition", "NodeList", "ReqCPUS", "AllocCPUS", "ReqMem", "AveRSS", "MaxRSS" ]
    #, "Command", "StdErr", "StdOut", "WorkDir"
    format_str = ",".join(fields)

    try:
        # Run scontrol command
        result = subprocess.run(["sacct", "-j", str(job_id), f"--format={format_str}", "--noheader"], capture_output=True, text=True, check=True)

    except subprocess.CalledProcessError:
        # Job not found or command failed
        return pd.DataFrame()
    
    output = result.stdout.strip()#.splitlines()
    # If there are no lines, the job is not in accounting DB yet
    #if len(output)==0:
    #    return pd.DataFrame()
    print(output)
    
    #first_line = next((line for line in output if line.strip()), None)
    #print(first_line)
    #if first_line is None:
    #    return pd.DataFrame()
    #parts1 = first_line.split()
    #print(parts1)
    
    #second_line = next((line for line in output if line.strip()), None)
    #print(second_line)
    #if second_line is None:
    #    return pd.DataFrame()
    #parts2 = second_line.split()
    #print(parts2)

    # If sacct gave fewer columns than expected
    #if len(parts) < len(fields):
        # pad missing values with empty strings
    #    parts = parts + [""] * (len(fields) - len(parts))

    #return pd.DataFrame({ "Field": fields, "Value": parts })
    
df = get_jobInfo_sacct(5886414)
#print(df)
#df = get_jobInfo_sacct(7777777)
#print(df)
#df = get_jobInfo_sacct(5896738)
#print(df)