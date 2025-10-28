# Private Crypter

This project is a private crypter designed to obfuscate Portable Executable (PE) files to bypass security software. It consists of two main components: a Builder and a Stub.

## Builder

The Builder is a C++ application that takes a source `.exe` file as input and produces an obfuscated executable. It encrypts the binary code of the source file using AES-256 and bundles the encrypted payload with the Stub.

## Stub

The Stub is a small decryption routine embedded in the obfuscated executable. It performs anti-analysis checks to detect sandboxes and debuggers, decrypts the payload in memory, and uses reflective loading to inject the payload into a legitimate process.

## Obfuscation Techniques

The crypter employs a range of advanced obfuscation techniques to make the generated executable difficult to analyze and detect:

- **Code Flow Obfuscation:** The Stub's execution flow is randomized to confuse static analysis tools.
- **String Obfuscation:** Critical strings, such as Windows API function names, are encoded and decrypted at runtime.
- **Metacompilation:** The Stub is compiled with randomized variable and function names to create a unique binary signature.
