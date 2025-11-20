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
    fields = [ "User", "JobName", "State", "ExitCode", "DerivedExitCode", "Elapsed", "Timelimit", "Submit", "Start", "End", "Partition", "NodeList", "WorkDir", "ReqCPUS", "AllocCPUS", "ReqMem", "AveRSS", "MaxRSS" ]
    format_str = ",".join(fields)

    try:
        # Run scontrol command
        result = subprocess.run(["sacct", "-j", str(job_id), f"--format={format_str}", "--units=G" , "--noheader", "--parsable2"], capture_output=True, text=True, check=True)

    except subprocess.CalledProcessError:
        # Job not found or command failed
        return pd.DataFrame()
    
    output = result.stdout.strip().splitlines()
    if len(output)<3:
        return pd.DataFrame()
    
    first_line = output[0].replace("sys/dashb+", "sys/dashb+ (ondemand)").split("|")
    #second_line = output[1].split("|")
    print(len(fields))
    print(len(first_line))
    print(first_line)
    #third_line = output[2]
    #if len(first_line)<len(fields) or len(second_line)<len(fields) or len(third_line)<len(fields):
    #    return pd.DataFrame()
    
    # Edit DF
    #df = pd.DataFrame({ "Field": fields, f"Value\n{}": parts })
    #df.loc[df["Field"]=="JobName", "Value"] = df.loc[df["Field"]=="JobName", "Value"].str.replace("sys/dashb+", "sys/dashb+ (ondemand)")
    
    #cpus = df.query("Field=='ReqCPUS'")["Value"].iloc[0]
    #mem = df.query("Field=='ReqMem'")["Value"].iloc[0]
    #nodes = len(df.query("Field=='NodeList'")["Value"].iloc[0].split(","))
    #new_row = {"Field": "ReqTRES", "Value":f"cpu={cpus},mem={mem},node={nodes}"}
    #df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    #df = df[~df['Field'].isin(["ReqMem", "ReqCPUS"])]

    #move_last = ["AllocCPUS", "AveRSS", "MaxRSS"]
    #mask = df['Field'].isin(move_last)
    #df = pd.concat([df[~mask], df[mask]], ignore_index=True)

    #dic_exitCodes = {
    #    "0:0":"Success",
    #    "1:0":"Application error",
    #    "0:15":"User cancelled job",
    #    "0:9":"Time limit reached, forced kill, OOM, admin kill",
    #    "137:0":"Job killed by SIGKILL - could be OOM or timeout",
    #    "0:271":"Node failure",
    #    "2:0":"CLI or arg parsing error in script"
    #}
    #for field in ["ExitCode", "DerivedExitCode"]:
    #    for code,desc in dic_exitCodes.items():
    #        df.loc[df["Field"]==field, "Value"] = df.loc[df["Field"]==field, "Value"].str.replace(code, f"{code} ({desc})")

    #df = df.reset_index(drop=True)

    #return df
    
#df = get_jobInfo_scontrol()
#print(df)

#df = get_jobInfo_sacct(5886414)
#print(df)
#print("\n")
#df = get_jobInfo_sacct(5896738)
#print(df)
get_jobInfo_sacct(5896738)