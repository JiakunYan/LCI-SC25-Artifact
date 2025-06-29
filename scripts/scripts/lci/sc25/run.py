#!/usr/bin/env python3

import os
import sys
sys.path.append("../../../include")
from script_common import *

default_config = {
    "name": "lci-bench",
    "root_packages": "lci2",
    "spack_env": "lcw-lci2-sc25",
    "nnodes": [1],
    "ntasks_per_node": 1,
    "window": 8,
}
time = 5

nthreads = [1, 2, 4, 8, 16, 32, 64, 128]

configs = [
    {**default_config, "name": "matching_engine", "nthreads": nthreads, "cmd": "lci_bench_matching_engine --niters 100000 --nthreads $config[nthreads] --window $config[window]"},
    {**default_config, "name": "packet_pool", "nthreads": nthreads, "cmd": "lci_bench_packet_pool --niters 100000 --nthreads $config[nthreads] --window $config[window]"},
    {**default_config, "name": "cq", "nthreads": nthreads, "cmd": "lci_bench_cq --niters 100000 --nthreads $config[nthreads] --window $config[window]"},
]

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    for i in range(n):
        submit_jobs(configs, all_inside=True, time=time)