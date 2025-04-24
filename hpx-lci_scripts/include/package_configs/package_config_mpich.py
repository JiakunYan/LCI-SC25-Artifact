from package_configs.package_config_base import *


class PackageConfigMpich(PackageConfigBase):
    name = "mpich"

    def get_dependency(self, config):
        return []

    def get_default_config(self, config):
        default = {
            "mpich:global_progress": 0,
        }
        if config["lcw:use_stream"]:
            default["mpich:nvcis_rsrv"] = config.get("hpx:ndevices", 0)
        else:
            default["mpich:nvcis"] = config.get("hpx:ndevices", 0)
        set_config_if_not_exist(config, default)
        return config

    def get_env_vars(self, config):
        ret = {}
        set_env_if_exist(ret, "MPIR_CVAR_CH4_GLOBAL_PROGRESS", config, "mpich:global_progress")
        set_env_if_exist(ret, "MPIR_CVAR_CH4_NUM_VCIS", config, "mpich:nvcis")
        set_env_if_exist(ret, "MPIR_CVAR_CH4_RESERVE_VCIS", config, "mpich:nvcis_rsrv")
        return ret

    def get_args(self, config):
        args = []
        return args


register_package(PackageConfigMpich())