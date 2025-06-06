cmake_minimum_required(VERSION 3.13)
project(ARL VERSION 0.5.0)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
enable_testing()

set(ARL_BACKEND gex CACHE STRING "Backend")
set_property(CACHE ARL_BACKEND PROPERTY STRINGS gex lci)
if(ARL_BACKEND STREQUAL "gex")
    set(ARL_USE_GEX ON)
elseif(ARL_BACKEND STREQUAL "lci")
    set(ARL_USE_LCI ON)
else()
    message(FATAL_ERROR "Fabric ${LCI_SERVER} not supported")
endif()

option(ARL_DEBUG "Enable debug mode" OFF)
option(ARL_INFO "Enable info mode" OFF)

LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake_modules")
include(ARLUtils)

find_package(Threads REQUIRED)

add_library(arl STATIC)
target_link_libraries(arl PUBLIC Threads::Threads)
add_subdirectory(include)
add_subdirectory(src)

find_package(LCI REQUIRED CONFIG PATH_SUFFIXES lib/cmake lib64/cmake)

if(ARL_USE_GEX)
    set(ARL_USE_GASNET_MODULE gasnet-ibv-par CACHE STRING "Gasnet module to use")
    set_property(CACHE ARL_USE_GASNET_MODULE PROPERTY STRINGS gasnet-aries-par gasnet-ibv-par gasnet-mpi-par gasnet-shm-par)
    option(ARL_USE_GASNET_NEED_MPI "Gasnet module needs MPI" ON)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(gasnet REQUIRED IMPORTED_TARGET ${ARL_USE_GASNET_MODULE})
    if (ARL_USE_GASNET_NEED_MPI)
        find_package(MPI REQUIRED)
        target_include_directories(arl PUBLIC MPI::MPI_CXX)
    endif()

    # fix a cmake bug when encountering multiple "--param <val>" options
    # Reference: https://cmake.org/cmake/help/latest/command/target_compile_options.html#option-de-duplication
    macro(fix_property TARGET PROPERTY)
        get_target_property(PROPERTY_OLD ${TARGET} ${PROPERTY})
        string(REPLACE "--param;" "SHELL:--param " PROPERTY_NEW "${PROPERTY_OLD}")
        set_target_properties(${TARGET} PROPERTIES ${PROPERTY} "${PROPERTY_NEW}")
        message(STATUS "Fix ${TARGET} ${PROPERTY}: ${PROPERTY_OLD} -> ${PROPERTY_NEW}")
    endmacro()
    fix_property(PkgConfig::gasnet INTERFACE_COMPILE_OPTIONS)
    fix_property(PkgConfig::gasnet INTERFACE_LINK_OPTIONS)
    target_link_libraries(arl PUBLIC PkgConfig::gasnet)
    target_link_libraries(arl PRIVATE LCI::lct)
elseif(ARL_USE_LCI)
    target_link_libraries(arl PUBLIC LCI::lci)
endif()

add_subdirectory(examples)
add_subdirectory(tests)