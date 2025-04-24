#!/bin/bash

git clone https://JiakunYan@bitbucket.org/berkeleylab/upcxx-utils.git

BUILD_THREADS=16 CPPFLAGS="$CPPFLAGS -fPIC -DGASNETI_FORCE_PIC=1" ./upcxx-utils/contrib/install_upcxx.sh $HOME/opt/upcxx-2023.9 --enable-ibv --with-pmi-version=2 --with-default-net=ibv --with-ibv-max-medium=65536 --enable-pmi --with-ibv-spawner=pmi --with-ibv-physmem-max=1/2 --disable-mpi-compat --with-ibv-max-hcas=3 --with-pmi-home=/cm/shared/apps/slurm/current --with-pmirun-cmd=srun