from script_common import *
import pshell
sys.path.append("..")
from platform_configs.platform_config_base import *

class PackageConfigBase:
    name = "base"

    def get_dependency(self, config):
        return []

    def get_default_config(self, config):
        return {}
    
    def get_env_vars(self, config):
        return []

    def get_args(self, config):
        return []
    
g_package_dict = {}

def register_package(package):
    assert not package.name in g_package_dict
    g_package_dict[package.name] = package

def get_default_config(config):
    assert "root_packages" in config
    todo_lists = config["root_packages"].split(",")
    done_lists = []
    ret = {}
    while len(todo_lists) > 0:
        name = todo_lists.pop(0)
        done_lists.append(name)
        package = g_package_dict[name]
        deps = package.get_dependency(config)
        for dep in deps:
            if dep not in done_lists:
                todo_lists.append(dep)

        ret.update(package.get_default_config(config))
    return ret

def get_env_vars(config):
    assert "root_packages" in config
    todo_lists = config["root_packages"].split(",")
    done_lists = []
    ret = {}
    while len(todo_lists) > 0:
        name = todo_lists.pop(0)
        done_lists.append(name)
        package = g_package_dict[name]
        deps = package.get_dependency(config)
        for dep in deps:
            if dep not in done_lists:
                todo_lists.append(dep)

        ret.update(package.get_env_vars(config))
    ret.update(get_platform_config("custom_env", config))
    return ret

def get_args(config):
    assert "root_packages" in config
    todo_lists = config["root_packages"].split(",")
    done_lists = []
    ret = []
    while len(todo_lists) > 0:
        name = todo_lists.pop(0)
        done_lists.append(name)
        package = g_package_dict[name]
        deps = package.get_dependency(config)
        for dep in deps:
            if dep not in done_lists:
                todo_lists.append(dep)

        ret += package.get_args(config)
    return ret

from package_configs.package_config_mpich import *
from package_configs.package_config_lci2 import *
from package_configs.package_config_lcw import *
from package_configs.package_config_lcw_pingpong import *
from package_configs.package_config_hpx import *
from package_configs.package_config_octotiger import *
from package_configs.package_config_arl import *
from package_configs.package_config_arl_kcount import *