cmake_minimum_required(VERSION 3.26)
project(KDS)

set(CMAKE_CXX_STANDARD 14)

include_directories(demos)
include_directories(include)
include_directories(src)

add_executable(KDS
        demos/init_test.cpp)
