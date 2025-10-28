cmake_minimum_required(VERSION 3.10)
project(Stub)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

include_directories(../vendor)

add_executable(stub src/main.cpp src/string_obfuscation.cpp src/reflective_loader.cpp)

# Link tegen de benodigde Windows-bibliotheken
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -luser32")

# --- Statisch linken ---
# Voeg de C++ en GCC bibliotheken statisch toe aan de executable.
# Dit zorgt ervoor dat de output.exe geen externe DLL's zoals
# libgcc_s_seh-1.dll of libstdc++-6.dll nodig heeft.
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -static-libgcc -static-libstdc++")
