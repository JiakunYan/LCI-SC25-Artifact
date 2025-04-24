from package_configs.package_config_base import *


class PackageConfigLcwpingpong(PackageConfigBase):
    name = "lcw_pingpong"

    def get_dependency(self, config):
        return ["lcw"]

    def get_default_config(self, config):
        default = {}
        set_config_if_not_exist(config, default)
        return config

    def get_env_vars(self, config):
        ret = {}
        return ret

    def get_args(self, config):
        args = []
        args = append_config_if_exist(args, "--op={}", config, "lcwpp:op")
        args = append_config_if_exist(args, "--ndevices={}", config, "lcwpp:ndevices")
        args = append_config_if_exist(args, "--nthreads={}", config, "lcwpp:nthreads")
        args = append_config_if_exist(args, "--min-size={}", config, "lcwpp:min_size")
        args = append_config_if_exist(args, "--max-size={}", config, "lcwpp:max_size")
        args = append_config_if_exist(args, "--niters={}", config, "lcwpp:niters")
        args = append_config_if_exist(args, "--test-mode={}", config, "lcwpp:test_mode")
        args = append_config_if_exist(args, "--pin-thread={}", config, "lcwpp:pin_thread")
        args = append_config_if_exist(args, "--nprgthreads={}", config, "lcwpp:nprgthreads")
        args = append_config_if_exist(args, "--send-window={}", config, "lcwpp:send_window")
        args = append_config_if_exist(args, "--recv-window={}", config, "lcwpp:recv_window")
        args = append_config_if_exist(args, "--compute-us={}", config, "lcwpp:compute_us")
        args = append_config_if_exist(args, "--compute-us-std={}", config, "lcwpp:compute_us_std")
        args = append_config_if_exist(args, "--max-progress-steps={}", config, "lcwpp:max_progress_steps")
        return ["lcw_pingpong_mt"] + args


register_package(PackageConfigLcwpingpong())