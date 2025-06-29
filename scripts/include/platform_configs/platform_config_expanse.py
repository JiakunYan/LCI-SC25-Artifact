import sys

sys.path.append("../../include")
# from platform_config_base import *
from platform_configs.platform_config_base import *

class ExpanseConfig(PlatformConfigBase):
    name = "expanse"
    network = "ibv"
    cpus_per_node = 128
    gpus_per_node = 0
    account = "uic193" # FIXME: Should be changed to your account
    partition = "compute"
    additional_sbatch_args = ["--mem=128G", "--constraint=\"lustre\""]
    octotiger_dataset_path = {
        "rs": "%root%/scripts/octotiger/data",
    } # FIXME: Should be changed to your dataset path
    hipmer_dataset_path = "/expanse/lustre/scratch/jackyan1/temp_project/hipmer-dataset/" # FIXME: Should be changed to your dataset path

    def get_srun_args(self, config):
        pmi = config.get("pmi", "pmi2")
        return ["srun", "--mpi=" + pmi]

    def custom_env(self, config):
        return {"PMI_MAX_VAL_SIZE": "512"} # Work around a MPICH bootstrap issue

