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

df = get_jobInfo_scontrol(5886414)
print(df)
df = get_jobInfo_scontrol(7777777)
print(df)