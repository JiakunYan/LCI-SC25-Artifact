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
        if platformConfig.name == "delta" and config["spack_env"] == "arl-gex":
            # special treatment for GASNet-EX to walk around SS11 bugs
            pshell.run("export GASNET_OFI_RECEIVE_BUFF_SIZE=recv")
            pshell.run("export FI_OFI_RXM_RX_SIZE=8192")
            pshell.run("export FI_CXI_DEFAULT_CQ_SIZE=13107200")
            pshell.run("export FI_MR_CACHE_MONITOR=memhooks")
            pshell.run("export FI_CXI_RX_MATCH_MODE=software")
            pshell.run("export FI_CXI_REQ_BUF_MIN_POSTED=10")
            pshell.run("export FI_CXI_REQ_BUF_SIZE=25165824")

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