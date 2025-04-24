#!/usr/bin/env python3
import os
import sys
import json
import time

# load root path
sys.path.append(os.path.join(os.environ["GJS_ROOT_PATH"], "include"))
import pshell
from script_common import *

sbatch_script_prelogue()

# load configuration
config_str = getenv_or("GJS_CONFIGS", None)
print(config_str)
config = json.loads(config_str)

if type(config) is list:
    configs = config
else:
    configs = [config]

start_time = time.time()
niters = 3
# We assume here every job has the same application
do_warmup = False
for i in range(niters):
    for config in configs:
        config = get_default_config(config)
        print("Config: " + json.dumps(config))
        pshell.update_env(get_env_vars(config))

        cmd = (get_platform_config("get_srun_args", config) + ["--time=1"] +
               get_platform_config("get_numactl_args", config) +
               get_args(config))
        if do_warmup:
            # warmup
            print("Warmup run")
            pshell.run(cmd, to_print=False)
            do_warmup = False
        output, _ = pshell.run(cmd)
        pattern = "Estimated throughput is (\S+) Mkmers/s"
        matches = re.findall(pattern, output)
        result0 = float(matches[0]) if len(matches) > 0 else -1
        result1 = float(matches[1]) if len(matches) > 1 else -1
        total = result0 + result1
        print("hpx-all result: {}-{}: throughput: {},{},{}".format(config["app_name"], config["rt_name"], result0, result1, (result0 + result1) / 2))
end_time = time.time()
print("Executed {} configs. Total time is {}s.".format(len(configs), end_time - start_time))