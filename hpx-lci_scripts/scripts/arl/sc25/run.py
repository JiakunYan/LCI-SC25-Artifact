#!/usr/bin/env python3
import sys
sys.path.append("../../../include")
from script_common import *

spack_env = "arl-lci"

default_config = {
    "name": "$config[app_name]-$config[rt_name]",
    "spack_env": spack_env,
    "platform": platformConfig.name,
    "arl:agg_buffer_type": "local",
    "arlkcount:dataset": "chr14-all",
    "lci2:cq_type": "array_atomic",
    "lci2:ibv_td_strategy": "all_qp",
    "arl:nprgthreads": 0,
    "arl:shared_cq": 1,
    "arl:max_buffer_size": 8192,
}

matrix_inside = []
time = 10
ntasks_per_node = 8

app_configs = [
    {"app_name": "kcount", "root_packages": "arl_kcount", "nnodes": [1, 2, 4, 8, 16, 32], "ntasks_per_node": ntasks_per_node},
]

rt_config = [
    {"rt_name": "lci-t64", "spack_env": "arl-lci", "arlkcount:backend": "lci", "ntasks_per_node": 2},
    {"rt_name": "gex-t64", "spack_env": "arl-gex", "arlkcount:backend": "gex", "ntasks_per_node": 2},
    {"rt_name": "gex-p1-t64", "spack_env": "arl-gex", "arlkcount:backend": "gex", "ntasks_per_node": 2, "arl:nprgthreads": 1},
    {"spack_env": "arl-gex", "rt_name": "upcxx", "arlkcount:backend": "upcxx", "ntasks_per_node": 128},
]

# update_outside = app_configs
# update_inside = rt_config
# configs = [default_config]
update_outside = None
update_inside = None
configs = dict_product(default_config, app_configs, rt_config)

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, matrix_inside, update_outside, update_inside, time=time)
