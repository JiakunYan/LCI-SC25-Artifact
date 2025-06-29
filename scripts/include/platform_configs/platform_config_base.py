import os, sys

class PlatformConfigBase:
    name = "None"
    network = "ibv"
    srun_pmi_option=[]
    cpus_per_node = 64
    gpus_per_node = 0
    cpus_per_core = 1
    numa_policy = "default"
    account = None
    partition = None
    additional_sbatch_args = []

    def get_numactl_args(self, config):
        args = []
        if self.numa_policy == "interleave":
            args = ["numactl", "--interleave=all"]
        return args

    def get_srun_args(self, config):
        return ["srun"]

    def custom_env(self, config):
        return {}

from platform_configs.platform_config_expanse import ExpanseConfig
from platform_configs.platform_config_delta import DeltaConfig

platformConfig = PlatformConfigBase()

if "CMD_WLM_CLUSTER_NAME" in os.environ and os.environ["CMD_WLM_CLUSTER_NAME"] == "expanse" or \
        "SLURM_CLUSTER_NAME" in os.environ and os.environ["SLURM_CLUSTER_NAME"] == "expanse":
    platformConfig = ExpanseConfig()
elif "HOSTNAME" in os.environ and "delta" in os.environ["HOSTNAME"] or \
        "SLURM_CLUSTER_NAME" in os.environ and os.environ["SLURM_CLUSTER_NAME"] == "delta":
    platformConfig = DeltaConfig()
# else:
#     print("Unknown platform!")
#     exit(1)

def get_platform_config(name, config, default=None):
    target = getattr(platformConfig, name, default)
    if callable(target):
        if type(config) is list:
            config = intersect_dicts(config)
        return target(config)
    else:
        return target