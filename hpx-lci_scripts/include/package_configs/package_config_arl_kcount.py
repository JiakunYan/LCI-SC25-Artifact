from package_configs.package_config_base import *


class PackageConfigArlKcount(PackageConfigBase):
    name = "arl_kcount"

    def get_dependency(self, config):
        return ["arl"]

    def get_default_config(self, config):
        default = {
            "arlkcount:kmer-len": 51,
            "arlkcount:dataset": "chr14-longjump",
            "arlkcount:backend": "lci",
        }
        set_config_if_not_exist(config, default)
        return config

    def get_env_vars(self, config):
        ret = {}
        return ret

    def get_args(self, config):
        #dataset
        dataset_path = platformConfig.hipmer_dataset_path
        dataset_dict = {
            "chr14-longjump": dataset_path + "hipmer_chr14_data/longjump.fastq",
            "chr14-shortjump": dataset_path + "hipmer_chr14_data/shortjump.fastq",
            "chr14-all": dataset_path + "hipmer_chr14_data/all.fastq",
        }
        reads_default = dataset_dict[config['arlkcount:dataset']]
        if not "arlkcount:reads" in config:
            config["arlkcount:reads"] = reads_default
        #backend
        if config["arlkcount:backend"] == "lci":
            executable = "arl_kcount_ffrd"
        elif config["arlkcount:backend"] == "gex":
            executable = "arl_kcount_ffrd"
        elif config["arlkcount:backend"] == "upcxx":
            executable = "arl_kcount_upcxx"
        else:
            raise ValueError("Invalid backend")
        
        args = []
        args = append_config_if_exist(args, "--kmer-len={}", config, "arlkcount:kmer-len")
        args = append_config_if_exist(args, "--reads={}", config, "arlkcount:reads")

        return [executable, "-v"] + args


register_package(PackageConfigArlKcount())