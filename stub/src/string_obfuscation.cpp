#include "string_obfuscation.h"

std::string deobfuscate(const std::vector<char>& obfuscated_string, char key) {
    std::string result;
    result.reserve(obfuscated_string.size());
    for (char c : obfuscated_string) {
        result += c ^ key;
    }
    return result;
}
