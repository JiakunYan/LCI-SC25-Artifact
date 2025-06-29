#!/usr/bin/env python3
import os
import sys
import json
import time

# load root path
sys.path.append(os.path.join(os.environ["GJS_ROOT_PATH"], "include"))
import pshell
from script_common import *

# load configuration
config_str = getenv_or("GJS_CONFIGS", None)
print(config_str)
config = json.loads(config_str)

if type(config) is list:
    configs = config
else:
    configs = [config]

pshell.run("cd run")

start_time = time.time()
nruns = 3
nwarmups = 1
for i in range(nruns):
    for config in configs:
        config = get_default_config(config)
        print("Config: " + json.dumps(config))
        pshell.update_env(get_env_vars(config))

        args = []
        args += ["--ntasks={}".format(int(config["ntasks_per_node"]))]
        args += ["--ntasks-per-node={}".format(int(config["ntasks_per_node"]))]
        args += ["--cpus-per-task={}".format(int(platformConfig.cpus_per_node / config["ntasks_per_node"]))]

        cmd = (["time"] + get_platform_config("get_srun_args", config) + args + ["--time=1"] +
               get_platform_config("get_numactl_args", config) + config["cmd"].split())
        if i < nwarmups:
            # warmup
            pshell.run(cmd, to_print=False)
        pshell.run(cmd)
end_time = time.time()
print("Executed {} configs. Total time is {}s.".format(len(configs), end_time - start_time))