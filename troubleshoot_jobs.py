import subprocess
import pandas as pd
import re

def get_slurm_job_info(job_id):
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
        return pd.DataFrame(columns=["Field", "Value"])

    output = result.stdout.strip()
    if not output or "JobId" not in output:
        # Job not in memory or invalid
        return pd.DataFrame(columns=["Field", "Value"])

    # Flatten multiline scontrol output
    output = re.sub(r'\s+', ' ', output)
    print(output)

    # Parse key=value pairs
    #data = dict(re.findall(r'(\S+?)=(\S+)', output))

    # Extract only requested fields
    #fields = [ "UserId", "Priority", "QOS", "JobState", "Reason", "RunTime", "TimeLimit", "SubmitTime", "EligibleTime", "StartTime", "EndTime", "Partition", "NodeList", "ReqTRES", "AllocTRES", "Command", "StdErr", "StdOut" ]
    #info = [(field, data.get(field, "")) for field in fields]

    # Return as DataFrame
    #return pd.DataFrame(info, columns=["Field", "Value"])

df = get_slurm_job_info(5886414)
print(df)