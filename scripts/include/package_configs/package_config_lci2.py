from package_configs.package_config_base import *


class PackageConfigLci(PackageConfigBase):
    name = "lci2"

    def get_dependency(self, config):
        return []

    def get_default_config(self, config):
        default = {}
        set_config_if_not_exist(config, default)
        return config

    def get_env_vars(self, config):
        ret = {
            "LCI_ATTR_NET_MAX_SENDS": "64",
            "LCI_ATTR_NET_MAX_RECVS": "1024",
            "LCI_ATTR_NPACKETS": "65536",
            "LCI_ATTR_NET_MAX_CQES": "65536",
            "LCI_ATTR_PACKET_SIZE": "8192",
        }
        set_env_if_exist(ret, "LCI_ATTR_USE_REG_CACHE", config, "lci2:use_reg_cache")
        set_env_if_exist(ret, "LCI_ATTR_USE_CONTROL_CHANNEL", config, "lci2:use_control_channel")
        set_env_if_exist(ret, "LCI_NETWORK_BACKEND_DEFAULT", config, "lci2:backend")
        set_env_if_exist(ret, "LCI_ATTR_NET_MAX_SENDS", config, "lci2:net_max_sends")
        set_env_if_exist(ret, "LCI_ATTR_NET_MAX_RECVS", config, "lci2:net_max_recvs")
        set_env_if_exist(ret, "LCI_ATTR_PACKET_SIZE", config, "lci2:packet_size")
        set_env_if_exist(ret, "LCI_ATTR_NPACKETS", config, "lci2:npackets")
        set_env_if_exist(ret, "LCI_ATTR_CQ_TYPE", config, "lci2:cq_type")
        set_env_if_exist(ret, "LCI_ATTR_IBV_TD_STRATEGY", config, "lci2:ibv_td_strategy")
        if get_platform_config("network", config) == "ss11":
            ret["LCI_ATTR_USE_REG_CACHE"] = 0
            ret["LCI_ATTR_USE_CONTROL_CHANNEL"] = 0
        return ret

    def get_args(self, config):
        args = []
        return args


register_package(PackageConfigLci())