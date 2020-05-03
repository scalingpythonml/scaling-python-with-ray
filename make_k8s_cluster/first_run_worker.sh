#!/bin/bash
/setup_k3s_worker.sh | tee /first_run.log
/setup_falco.sh |tee /first_run.log
rm $0
