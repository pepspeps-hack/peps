cmake_minimum_required(VERSION 3.10)
project(Builder)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

include_directories(../vendor)

add_executable(builder src/main.cpp)
