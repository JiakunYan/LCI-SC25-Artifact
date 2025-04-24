from package_configs.package_config_base import *


class PackageConfigLcw(PackageConfigBase):
    name = "lcw"

    def get_dependency(self, config):
        if "lcw:backend" in config:
            if config["lcw:backend"] == "mpi":
                return ["mpich"]
            elif config["lcw:backend"] == "lci":
                return ["lci"]
            else:
                return ["lci2"]
        else:
            return ["lci"]

    def get_default_config(self, config):
        default = {
            "lcw:backend": "mpi",
            "lcw:use_stream": 0,
            "lcw:comp_type": "cont",
            "lcw:use_cont_imm": 1,
            "lcw:use_cont_req": 0,
        }
        set_config_if_not_exist(config, default)
        return config

    def get_env_vars(self, config):
        ret = {}
        set_env_if_exist(ret, "LCW_BACKEND_AUTO", config, "lcw:backend")
        set_env_if_exist(ret, "LCW_MPI_USE_STREAM", config, "lcw:use_stream")
        set_env_if_exist(ret, "LCW_MPI_COMP_TYPE", config, "lcw:comp_type")
        set_env_if_exist(ret, "LCW_MPI_CONT_IMM", config, "lcw:use_cont_imm")
        set_env_if_exist(ret, "LCW_MPI_CONT_REQ", config, "lcw:use_cont_req")
        set_env_if_exist(ret, "LCW_MPI_NUM_COMP_MANAGERS", config, "lcw:ncomps")
        set_env_if_exist(ret, "LCW_MPI_MAX_PENDING_MSG", config, "lcw:max_pending_msg")
        return ret

    def get_args(self, config):
        args = []
        return args


register_package(PackageConfigLcw())