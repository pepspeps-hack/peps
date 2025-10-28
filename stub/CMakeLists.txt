cmake_minimum_required(VERSION 3.10)
project(Stub)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

include_directories(../vendor)

add_executable(stub src/main.cpp src/string_obfuscation.cpp src/reflective_loader.cpp)

# Link against user32 for MessageBoxA
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -luser32")
