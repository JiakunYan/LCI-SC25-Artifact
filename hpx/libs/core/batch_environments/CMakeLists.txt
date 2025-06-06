# Copyright (c) 2019-2022 The STE||AR-Group
#
# SPDX-License-Identifier: BSL-1.0
# Distributed under the Boost Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

set(batch_environments_headers
    hpx/batch_environments/alps_environment.hpp
    hpx/batch_environments/batch_environment.hpp
    hpx/batch_environments/pjm_environment.hpp
    hpx/batch_environments/pbs_environment.hpp
    hpx/batch_environments/slurm_environment.hpp
)

# cmake-format: off
set(batch_environments_compat_headers
    hpx/batch_environments.hpp => hpx/modules/batch_environments.hpp
    hpx/util/batch_environment.hpp => hpx/modules/batch_environments.hpp
    hpx/util/batch_environments/alps_environment.hpp => hpx/modules/batch_environments.hpp
    hpx/util/batch_environments/pbs_environment.hpp => hpx/modules/batch_environments.hpp
    hpx/util/batch_environments/slurm_environment.hpp => hpx/modules/batch_environments.hpp
)
# cmake-format: on

set(batch_environments_sources
    alps_environment.cpp batch_environment.cpp pbs_environment.cpp
    pjm_environment.cpp slurm_environment.cpp
)

include(HPX_AddModule)
add_hpx_module(
  core batch_environments
  GLOBAL_HEADER_GEN ON
  SOURCES ${batch_environments_sources}
  HEADERS ${batch_environments_headers}
  COMPAT_HEADERS ${batch_environments_compat_headers}
  MODULE_DEPENDENCIES
    hpx_config
    hpx_assertion
    hpx_format
    hpx_string_util
    hpx_errors
    hpx_asio
    hpx_type_support
  CMAKE_SUBDIRS examples tests
)

# see #6579
if(MSVC AND Boost_VERSION_STRING VERSION_LESS "1.79.0")
  target_compile_definitions(hpx_batch_environments PRIVATE NOMINMAX)
endif()
