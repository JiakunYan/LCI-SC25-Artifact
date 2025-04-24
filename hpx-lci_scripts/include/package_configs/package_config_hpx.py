from package_configs.package_config_base import *


class PackageConfigHpx(PackageConfigBase):
    name = "hpx"

    def get_dependency(self, config):
        ret = []
        if config["hpx:parcelport"] == "lci":
            ret.append("lci")
        elif config["hpx:parcelport"] == "lcw":
            ret.append("lcw")
        return ret

    def get_default_config(self, config):
        default = {
            "hpx:zc_threshold": 8192,
            "hpx:parcelport": "lci",
            "hpx:protocol": "putva",
            "hpx:comp_type": "queue",
            "hpx:progress_type": "rp",
            "hpx:progress_strategy": "local",
            "hpx:sendimm": 1,
            "hpx:backlog_queue": 0,
            "hpx:prg_thread_core": -1,
            "hpx:prepost_recv_num": 1,
            "hpx:zero_copy_recv": 1,
            "hpx:in_buffer_assembly": 1,
            "hpx:reg_mem": 0,
            "hpx:ndevices": 1,
            "hpx:ncomps": 1,
        }
        set_config_if_not_exist(config, default)
        return config

    def get_env_vars(self, config):
        ret = {}
        if "hpx:reg_mem" in config and config["hpx:reg_mem"] or config["hpx:progress_type"] == "worker":
            # We only use the registration cache when only one progress thread is doing the registration.
            ret["LCI_USE_DREG"] = "0"
        return ret

    def get_args(self, config):
        def append_pp_config_if_exist(args, arg, config, key, parcelports):
            if key in config and config["hpx:parcelport"] in parcelports:
                args.append(arg.format(config["hpx:parcelport"], config[key]))
            return args
        args = [
            "--hpx:ini=hpx.stacks.use_guard_pages=0",
            f"--hpx:ini=hpx.parcel.{config['hpx:parcelport']}.priority=1000",
        ]
        nthreads_default = int(platformConfig.cpus_per_node / platformConfig.cpus_per_core / config.get('ntasks_per_node', 1))
        nthreads = config.get("hpx:nthreads", nthreads_default)
        if nthreads:
            args.append(f"--hpx:threads={nthreads}")

        args = append_config_if_exist(args, "--hpx:ini=hpx.agas.use_caching={}", config, "hpx:agas_caching")
        args = append_config_if_exist(args, "--hpx:ini=hpx.parcel.zero_copy_receive_optimization={}", config,
                                      "hpx:zero_copy_recv")
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.zero_copy_serialization_threshold={}",
                                         config, "hpx:zc_threshold", ["mpi", "lci", "lcw"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.sendimm={}", config,
                                         "hpx:sendimm", ["mpi", "lci", "lcw"])
        if "hpx:prg_thread_num" in config:
            if config["hpx:prg_thread_num"] == "auto":
                config["hpx:prg_thread_num"] = config["hpx:ndevices"]
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.protocol={}", config,
                                         "hpx:protocol", ["lci"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.comp_type_header={}", config,
                                         "hpx:comp_type_header", ["lci"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.comp_type_followup={}", config,
                                         "hpx:comp_type_followup", ["lci"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.prepost_recv_num={}", config,
                                         "hpx:prepost_recv_num", ["lci"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.reg_mem={}", config,
                                         "hpx:reg_mem", ["lci"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.enable_in_buffer_assembly={}", config,
                                         "hpx:in_buffer_assembly", ["lci"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.prg_thread_num={}", config,
                                         "hpx:prg_thread_num", ["lci", "lcw"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.progress_type={}", config,
                                         "hpx:progress_type", ["lci", "lcw"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.progress_strategy={}", config,
                                         "hpx:progress_strategy", ["lci", "lcw"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.backlog_queue={}", config,
                                         "hpx:backlog_queue", ["lci", "lcw"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.ndevices={}", config,
                                         "hpx:ndevices", ["lci", "lcw"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.ncomps={}", config,
                                         "hpx:ncomps", ["lci", "lcw"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.send_nb_max_retry={}", config,
                                         "hpx:send_nb_max_retry", ["lci"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.mbuffer_alloc_max_retry={}", config,
                                         "hpx:mbuffer_alloc_max_retry", ["lci"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.bg_work_when_send={}", config,
                                         "hpx:bg_work_when_send", ["lci"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.bg_work_max_count={}", config,
                                         "hpx:bg_work_max_count", ["lci"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.enable_sendmc={}", config,
                                         "hpx:enable_sendmc", ["lci"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.zero_copy_optimization={}", config,
                                         "hpx:zero_copy_optimization", ["mpi", "lci"])
        args = append_pp_config_if_exist(args, "--hpx:ini=hpx.parcel.{}.ndevices_fake={}", config,
                                         "hpx:ndevices_fake", ["lci"])
        return args


register_package(PackageConfigHpx())