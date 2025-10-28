#ifndef REFLECTIVE_LOADER_H
#define REFLECTIVE_LOADER_H

#include <windows.h>
#include <vector>
#include <cstdint>

// Main function to perform reflective loading
bool reflective_load(const std::vector<uint8_t>& payload);

#endif // REFLECTIVE_LOADER_H
