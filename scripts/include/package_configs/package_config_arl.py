from package_configs.package_config_base import *


class PackageConfigArl(PackageConfigBase):
    name = "arl"

    def get_dependency(self, config):
        return ["lci2"]

    def get_default_config(self, config):
        default = {}
        set_config_if_not_exist(config, default)
        return config

    def get_env_vars(self, config):
        # nthreads
        nthreads_default = int(platformConfig.cpus_per_node / platformConfig.cpus_per_core / config.get('ntasks_per_node', 1))
        if not "arl:nthreads" in config:
            config["arl:nthreads"] = nthreads_default
        # nprgthreads
        nprgthreads_default = 1
        if not "arl:nprgthreads" in config:
            config["arl:nprgthreads"] = nprgthreads_default
        # nworkers
        nworkers_default = config["arl:nthreads"] - config["arl:nprgthreads"]
        if not "arl:nworkers" in config:
            config["arl:nworkers"] = nworkers_default

        ret = {
            "ARL_PIN_THREAD": "1",
            "ARL_MAX_BUFFER_SIZE": "8192",
            "ARL_AGG_BUFFER_TYPE": "atomic",
        }
        set_env_if_exist(ret, "ARL_PIN_THREAD", config, "arl:pin_thread")
        set_env_if_exist(ret, "ARL_MAX_BUFFER_SIZE", config, "arl:max_buffer_size")
        set_env_if_exist(ret, "ARL_AGG_BUFFER_TYPE", config, "arl:agg_buffer_type")
        set_env_if_exist(ret, "ARL_LCI_SHARED_CQ", config, "arl:shared_cq")
        set_env_if_exist(ret, "ARL_LCI_SHARED_PROGRESS", config, "arl:shared_progress")
        set_env_if_exist(ret, "ARL_LCI_NDEVICES", config, "arl:ndevices")
        set_env_if_exist(ret, "ARL_LCI_MAX_SENDS", config, "arl:max_sends")
        set_env_if_exist(ret, "ARL_NWORKERS", config, "arl:nworkers")
        set_env_if_exist(ret, "ARL_NTHREADS", config, "arl:nthreads")
        return ret

    def get_args(self, config):
        args = []
        return args


register_package(PackageConfigArl())