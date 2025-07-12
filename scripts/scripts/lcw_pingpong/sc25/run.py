#!/usr/bin/env python3

import os
import sys
sys.path.append("../../../include")
from script_common import *

default_config = {
    "name": "$config[app_name]-$config[rt_name]",
    "root_packages": "lcw_pingpong",
    "spack_env": "lcw-lci-sc25",
    "nnodes": [2],
    "ntasks_per_node": 1,
    "lcwpp:op": "send",
    "lcwpp:nthreads": 64,
    "lcwpp:min_size": 8,
    "lcwpp:max_size": 8,
    "lcwpp:test_mode": 0,
    "lcwpp:niters": 100000,
    "lcwpp:ndevices": 1,
    "lcwpp:nprgthreads": 0,
    "lcwpp:send_window": 1,
    "lcwpp:recv_window": 1,
    "lcwpp:compute_us": 0,
    "lcw:backend": "mpi",
    "lcw:comp_type": "req",
    "lcw:ncomps": 0,
    "mpich:nvcis": "$config[lcwpp:ndevices]",
    "lcw:max_pending_msg": 0,
    "lci2:ibv_td_strategy": "all_qp",
    "lci2:net_max_sends": 256,
    "lci2:net_max_recvs": 256,
    "lci2:packet_size": "65664"
}
matrix_inside = ["lcwpp:nthreads", "ntasks_per_node", "lcwpp:min_size"]
time = 20

nthreads = [1, 2, 4, 8, 16, 32, 64, 128]

app_configs = [
    {"app_name": "lt-p$config[ntasks_per_node]", "ntasks_per_node": nthreads,"lcwpp:nthreads": [1], "lcwpp:ndevices": "$config[lcwpp:nthreads]", "lcwpp:op": "put", "lci2:npackets": 8192, "lci2:ibv_td_strategy": "none"},
    {"app_name": "lt-t$config[lcwpp:nthreads]", "ntasks_per_node": 1,"lcwpp:nthreads": nthreads, "lcwpp:ndevices": "$config[lcwpp:nthreads]", "lcwpp:op": "put"},
    {"app_name": "lt-t$config[lcwpp:nthreads]-d1", "ntasks_per_node": 1,"lcwpp:nthreads": [1, 2, 4, 8, 16, 32, 64, 128], "lcwpp:ndevices": "1", "lcwpp:op": "put"},
    {"app_name": "bw-p64-$config[lcwpp:min_size]", "ntasks_per_node": 64, "lcwpp:nthreads": [1], "lcwpp:ndevices": "$config[lcwpp:nthreads]", "lcwpp:min_size": [16, 64, 256, 1024, 4096, 16384, 65536, 262144, 1048576], "lcwpp:max_size": "$config[lcwpp:min_size]", "lcwpp:niters": 1000, "lci2:npackets": 8192},
    {"app_name": "bw-t64-$config[lcwpp:min_size]", "ntasks_per_node": 1, "lcwpp:nthreads": [64], "lcwpp:ndevices": "$config[lcwpp:nthreads]", "lcwpp:min_size": [16, 64, 256, 1024, 4096, 16384, 65536, 262144, 1048576], "lcwpp:max_size": "$config[lcwpp:min_size]", "lcwpp:niters": 1000},
    {"app_name": "bw-t64-$config[lcwpp:min_size]-d1", "ntasks_per_node": 1, "lcwpp:nthreads": [64], "lcwpp:ndevices": "$config[lcwpp:nthreads]", "lcwpp:min_size": [16, 64, 256, 1024, 4096, 16384, 65536, 262144, 1048576], "lcwpp:max_size": "$config[lcwpp:min_size]", "lcwpp:niters": 1000, "lcwpp:ndevices": "1"}
]

rt_configs = [
    {"rt_name": "lci", "lcw:backend": "lci2"},
    {"rt_name": "mpi", "lcw:backend": "mpi"},
    {"rt_name": "gex", "lcw:backend": "gex", "lcwpp:op": "put", "when": lambda config: "lt" in config["app_name"]},
    {"rt_name": "mpi-ucx", "lcw:backend": "mpi", "spack_env": "lcw-mpi-ucx-sc25", "when": lambda config: platformConfig.name == "expanse"}, # FIXME Platform: update platform name if necessary
    {"rt_name": "cray-mpich", "lcw:backend": "mpi", "spack_env": "lcw-cray-mpich-sc25", "when": lambda config: platformConfig.name == "delta"}, # FIXME Platform: update platform name if necessary
]

# update_outside = app_configs
# update_inside = rt_configs
# configs = [default_config]
update_outside = None
update_inside = None
configs = dict_product(default_config, app_configs, rt_configs)

filtered_configs = []
for config in configs:
    if "when" in config:
        if not config["when"](config):
            continue
        del config["when"]
    filtered_configs.append(config)
configs = filtered_configs

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    for i in range(n):
        submit_jobs(configs, matrix_inside, update_outside, update_inside, time=time)