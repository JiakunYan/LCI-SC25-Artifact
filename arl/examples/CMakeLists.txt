find_package(UPCXX QUIET CONFIG HINTS share/cmake/UPCXX)

add_arl_executable(arl_hello_world arl_hello_world.cpp)
add_arl_executable(counter counter.cpp)

add_subdirectory(microbenchmark)
add_subdirectory(kcount)
add_subdirectory(kmer_hash)