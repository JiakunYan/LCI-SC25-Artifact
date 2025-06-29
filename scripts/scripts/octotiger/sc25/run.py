#!/usr/bin/env python3
import sys
sys.path.append("../../../include")
from script_common import *

spack_env = "hpx-lci2-sc25"
lci_optimal_ndevices=2
lcw_optimal_ndevices=8
ntasks_per_node=2

default_config = {
    "name": "$config[app_name]-$config[rt_name]",
    "spack_env": spack_env,
    "platform": platformConfig.name,
    "hpx:parcelport": "lci",
    "hpx:zc_threshold": 8000,
    "hpx:protocol": "putsendrecv",
    "hpx:progress_type": "worker",
    "hpx:prg_thread_num": "auto",
    "hpx:sendimm": 1,
    "hpx:backlog_queue": 0,
    "hpx:prepost_recv_num": 1,
    "hpx:zero_copy_recv": 1,
    "hpx:reg_mem": 1,
    "hpx:ndevices": 2,
    "hpx:ncomps": 1,
    "lcw:backend": "lci2",
    "lci:device_lock_mode": "none",
    "lcw:use_cont_imm": 1, 
    "lcw:use_cont_req": 0,
    "lcw:ncomps": 0,
    "mpich:global_progress": 0,
}
if platformConfig.name == "expanse":
    lci_optimal_ndevices = 1
    lcw_optimal_ndevices = 8
    lcw_ncomps = [1, 2, 4, 8]
elif platformConfig.name == "delta":
    lci_optimal_ndevices = 2
    lcw_optimal_ndevices = 8
    lcw_ncomps = [1, 2, 4, 8]

matrix_inside = ["hpx:ndevices", "hpx:ncomps", "lcw:ncomps", "hpx:nthreads"]
time = 10

app_configs = [
    {"app_name": "octotiger", "root_packages": "octotiger", "nnodes": [1, 2, 4, 8, 16, 32], "ntasks_per_node": ntasks_per_node, "ot:griddim": 8, "ot:max_level": 5, "ot:stop_step": 20, "ot:scenario": "rs", "hpx:nthreads": 63},
]

rt_configs = [
    {"rt_name": "lci2", "hpx:parcelport": "lcw", "lcw:backend": "lci2", "hpx:ndevices": lci_optimal_ndevices},
    {"rt_name": "mpix", "hpx:parcelport": "lcw", "lcw:backend": "mpi", "hpx:ndevices": lcw_optimal_ndevices, "lcw:comp_type": "req", "lcw:ncomps": 0},
    {"rt_name": "mpi", "hpx:parcelport": "mpi"},
]

# update_outside = app_configs
# update_inside = rt_configs
# configs = [default_config]
update_outside = None
update_inside = None
configs = dict_product(default_config, app_configs, rt_configs)

if __name__ == "__main__":
    n = 1
    if len(sys.argv) > 1:
        n = int(sys.argv[1])

    mkdir_s("./run")

    os.environ["CURRENT_SCRIPT_PATH"] = os.path.dirname(os.path.realpath(__file__))

    for i in range(n):
        submit_jobs(configs, matrix_inside, update_outside, update_inside, time=time)
