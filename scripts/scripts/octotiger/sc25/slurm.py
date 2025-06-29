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

start_time = time.time()
niters = 3
do_warmup = False
for i in range(niters):
    for config in configs:
        config = get_default_config(config)
        print("Config: " + json.dumps(config))
        pshell.update_env(get_env_vars(config))

        if config["app_name"] == "octotiger":
            scenario = config.get("ot:scenario", "rs")
            octotiger_dataset_path = get_platform_config("octotiger_dataset_path", config)[scenario].replace("%root%", get_root_path())
            pshell.run(f"cd {octotiger_dataset_path}")

        cmd = (get_platform_config("get_srun_args", config) + ["--time=3"] +
               get_platform_config("get_numactl_args", config) +
               get_args(config)
               )
        if do_warmup:
            # warmup
            print("Warmup run")
            pshell.run(cmd, to_print=False)
            do_warmup = False
        output, _ = pshell.run(cmd)
        pattern = "Total: (\d+.\d+)"
        key = "runtime"
        m = re.search(pattern, output)
        print("hpx-all result: {}-{}: {}: {}".format(config["app_name"], config["rt_name"], key, m.group(1) if m else "N/A"))
end_time = time.time()
print("Executed {} configs. Total time is {}s.".format(len(configs), end_time - start_time))