#ifndef STRING_OBFUSCATION_H
#define STRING_OBFUSCATION_H

#include <string>
#include <vector>

// Simple XOR-based string obfuscation
std::string deobfuscate(const std::vector<char>& obfuscated_string, char key);

#endif // STRING_OBFUSCATION_H
