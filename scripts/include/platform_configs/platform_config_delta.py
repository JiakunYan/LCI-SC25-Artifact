import sys
sys.path.append("../../include")
# from platform_config_base import *
from platform_configs.platform_config_base import *

class DeltaConfig(PlatformConfigBase):
    name = "delta"
    network = "ss11"
    cpus_per_node = 128
    gpus_per_node = 0
    cpus_per_core = 1
    account = "bert-delta-cpu" # FIXME: Should be changed to your account
    partition = "cpu"
    qos = None
    octotiger_dataset_path = {
        "rs": "%root%/scripts/octotiger/data",
    } # FIXME: Should be changed to your dataset path
    hipmer_dataset_path = "/scratch/bert/jiakuny/hipmer-dataset/" # FIXME: Should be changed to your dataset path

    @property
    def additional_sbatch_args(self):
        return ["--exclusive", "--mem=0"]

    def get_srun_args(self, config):
        return ["srun"]

    def custom_env(self, config):
        return {}

