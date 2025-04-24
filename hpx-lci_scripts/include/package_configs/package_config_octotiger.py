from package_configs.package_config_base import *


def get_theta(config):
    griddim = config["ot:griddim"]
    if griddim >= 5:
        theta = 0.34
    elif 3 <= griddim <= 4:
        theta = 0.51
    elif 1 <= griddim <= 2:
        theta = 1.01
    else:
        print("invalid griddim {}!".format(griddim))
        exit(1)
    return theta

class PackageConfigOctotiger(PackageConfigBase):
    name = "octotiger"

    def get_dependency(self, config):
        ret = ["hpx"]
        return ret

    def get_default_config(self, config):
        default = {
            "ot:griddim": 8,
            "ot:scenario": "rs",
            "ot:max_level": 6,
        }
        set_config_if_not_exist(config, default)
        return config

    def get_env_vars(self, config):
        ret = {}
        return ret

    def get_args(self, config):
        args = [
            "--disable_output=on",
            "--amr_boundary_kernel_type=AMR_OPTIMIZED",
            "--optimize_local_communication=1",
            "--hpx:ini=hpx.parcel.zero_copy_optimization=0",
            "--print_times_per_timestep=1",
            # "--hpx:print-counter=/octotiger*/compute/gpu*kokkos*",
            # "--hpx:print-counter=/arithmetics/add@/octotiger*/compute/gpu/hydro_kokkos",
            # "--hpx:print-counter=/arithmetics/add@/octotiger*/compute/gpu/hydro_kokkos_aggregated",
        ]

        if config["ot:scenario"] == "rs":
            config_filename = "rotating_star.ini"
        elif config["ot:scenario"] == "gr":
            config_filename = "sphere.ini"
        elif "dwd" in config["ot:scenario"]:
            config_filename = "dwd.ini"
        else:
            print("Unknown task!")
            exit(1)
        args.append(f"--config_file={config_filename}")

        if "dwd" not in config["ot:scenario"]:
            args = append_config_if_exist(args, "--max_level={}", config, "ot:max_level")
            args.append(f"--theta={get_theta(config)}")
            args.append("--correct_am_hydro=0")

        ngpus_to_use = config.get("ngpus", get_platform_config("gpus_per_node", config, 0))
        if platformConfig.name == "ookami":
            args += [
                "--monopole_host_kernel_type=KOKKOS",
                "--multipole_host_kernel_type=KOKKOS",
                "--hydro_host_kernel_type=KOKKOS",
                "--monopole_device_kernel_type=OFF",
                "--multipole_device_kernel_type=OFF",
                "--hydro_device_kernel_type=OFF"
            ]
        elif ngpus_to_use == 0:
            args += [
                "--monopole_host_kernel_type=LEGACY",
                "--multipole_host_kernel_type=LEGACY",
                "--hydro_host_kernel_type=LEGACY",
                "--monopole_device_kernel_type=OFF",
                "--multipole_device_kernel_type=OFF",
                "--hydro_device_kernel_type=OFF"
            ]
        else:
            args += [
                f"--number_gpus={ngpus_to_use}",
                "--executors_per_gpu=128",
                "--monopole_host_kernel_type=DEVICE_ONLY",
                "--multipole_host_kernel_type=DEVICE_ONLY",
                "--hydro_host_kernel_type=DEVICE_ONLY",
                "--monopole_device_kernel_type=KOKKOS_CUDA",
                "--multipole_device_kernel_type=KOKKOS_CUDA",
                "--hydro_device_kernel_type=KOKKOS_CUDA",
                "--max_kernels_fused=4",
            ]

        args = append_config_if_exist(args, "--stop_step={}", config, "ot:stop_step")
        return ["octotiger"] + args


register_package(PackageConfigOctotiger())
