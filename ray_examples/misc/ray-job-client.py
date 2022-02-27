from ray.dashboard.modules.job.sdk import JobSubmissionClient
from ray.dashboard.modules.job.common import JobStatus

import time

client = JobSubmissionClient("http://raycluster-ray.borisdata-cluster-2a0beb393d3242574412e5315d3d4662-0000.us-south.containers.appdomain.cloud")

job_id = client.submit_job(
    # Entrypoint shell command to execute
    entrypoint="python script_with_parameters.py --kwargs iterations=7",
    # Working dir
    runtime_env={
        "working_dir": ".",
        "pip": ["requests==2.26.0", "qiskit==0.34.2"],
        "env_vars": {"MY_VARIABLE1": "foo", "MY_VARIABLE2": "bar"}
    }
)

print(f"Submitted job with ID : {job_id}")

while True:
    status_info = client.get_job_status(job_id)
    status = status_info.status
    print(f"status: {status}")
    if status in {JobStatus.SUCCEEDED, JobStatus.STOPPED, JobStatus.FAILED}:
        break
    time.sleep(5)

logs = client.get_job_logs(job_id)
print(f"logs: {logs}")