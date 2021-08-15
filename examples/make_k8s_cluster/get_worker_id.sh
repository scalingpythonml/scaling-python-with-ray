#!/bin/bash
flock -x -w 5 /worker_counter.txt sh -c 'COUNTER=$(cat /worker_counter.txt); echo $((COUNTER + 1)) > /worker_counter.txt; cat /worker_counter.txt'
