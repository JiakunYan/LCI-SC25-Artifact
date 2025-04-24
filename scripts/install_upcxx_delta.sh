#!/bin/bash

git clone https://JiakunYan@bitbucket.org/berkeleylab/upcxx-utils.git

BUILD_THREADS=16 CPPFLAGS="$CPPFLAGS -fPIC -DGASNETI_FORCE_PIC=1" ./upcxx-utils/contrib/install_upcxx.sh $HOME/opt/upcxx-2023.9 --enable-ofi --with-default-net=ofi --with-ofi-spawner=pmi --disable-mpi-compat --with-ofi-provider=cxi --with-ofi-max-medium=65536 --with-pmi-version=2 --with-pmirun-cmd=srun --disable-ibv