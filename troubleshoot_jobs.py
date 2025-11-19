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

    # Edit DF
    df = pd.DataFrame(info, columns=["Field", "Value"])
    df = df[~df["Value"].isin([None, '', "(null)", "None"])]
    for col in ["ReqTRES", "AllocTRES"]:
        df.loc[df["Field"]==col, "Value"] = df.loc[df["Field"]==col, "Value"].str.replace(r',billing=.*$', '', regex=True)
    df.loc[df["Field"]=="UserId", "Value"] = df.loc[df["Field"]=="UserId", "Value"].str.replace(r'\(.*$', '', regex=True)
    df = df.reset_index(drop=True)

    return df

# Better to use for failed or completed jobs
def get_jobInfo_sacct(job_id):
    """
    Get selected job information from sacct for a given job ID.
    Returns a pandas DataFrame with columns ['Field', 'Value'].
    Returns an empty DataFrame if no sacct data exists yet.
    """
    fields = [ "User", "State", "ExitCode", "DerivedExitCode", "Elapsed", "Timelimit", "Submit", "Start", "End", "Partition", "NodeList", "WorkDir", "JobName", "ReqCPUS", "AllocCPUS", "ReqMem", "AveRSS", "MaxRSS" ]
    format_str = ",".join(fields)

    try:
        # Run scontrol command
        result = subprocess.run(["sacct", "-j", str(job_id), f"--format={format_str}", "--units=G" , "--noheader"], capture_output=True, text=True, check=True)

    except subprocess.CalledProcessError:
        # Job not found or command failed
        return pd.DataFrame()
    
    output = result.stdout.strip().splitlines()
    # If there are no lines, the job is not in accounting DB yet
    if len(output)==0:
        return pd.DataFrame()
    
    first_line = output[0]
    second_line = output[1] if len(output)>1 else None
    if (first_line is None) or (second_line is None):
        return pd.DataFrame()
    
    if first_line.split()[1]!="RUNNING":
        parts = first_line.split()+second_line.split()[-2:]
    else:
        parts = first_line.split()
        fields = fields[:-2]
    if len(parts)<len(fields):
        return pd.DataFrame()
    
    # Edit DF
    df = pd.DataFrame({ "Field": fields, "Value": parts })
    df.loc[df["Field"]=="JobName", "Value"] = df.loc[df["Field"]=="JobName", "Value"].str.replace("sys/dashb+", "sys/dashb+ (ondemand)")
    cpus = df.query("Field=='ReqCPUS'")["Value"].iloc[0]
    mem = df.query("Field=='ReqMem'")["Value"].iloc[0]
    nodes = len(df.query("Field=='NodeList'")["Value"].iloc[0].split(","))
    new_row = {"Field": "ReqTRES", "Value":f"cpu={cpus},mem={mem},node={nodes}"}
    print(new_row)

    return df
    
df = get_jobInfo_sacct(5886414)
print(df)
#df = get_jobInfo_sacct(7777777)
#print(df)
print("\n")
df = get_jobInfo_sacct(5896738)
print(df)
    
#df = get_jobInfo_scontrol(5886414)
#print(df)
#df = get_jobInfo_scontrol(7777777)
#print(df)
#df = get_jobInfo_scontrol(5896738)
#print(df)