#!/bin/bash
/first_run.sh | tee /first_run.log
/setup_k3s_master.sh | tee /first_run.log
rm $0
