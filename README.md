Nyx is an advanced, polymorphic, multi-stage crypter for Python, designed for educational purposes in the fields of malware analysis, reverse engineering, and defensive security research. It transforms a standard Python script into a stealthy, multi-layered loader engineered to evade detection by both static and dynamic analysis tools.

Disclaimer: This tool is intended for academic and research purposes only. The author is not responsible for any misuse or damage caused by this program. Unauthorized use of this tool on systems you do not own is illegal.

Features
Nyx employs a sophisticated, layered approach to conceal and execute Python payloads, making it a powerful tool for understanding modern evasion techniques.

Polymorphic Code Generation: Each build produces a loader with a unique signature. Variable and function names are randomized, rendering signature-based detection ineffective.
Multi-Stage Execution: The payload is executed through a chain of in-memory loaders. The initial loader (Stage 1) only contains logic to decrypt the next stage, keeping the final payload deeply hidden.
Loader (Stage 1) -> AES Decryptor (Stage 2) -> Final Payload (Stage 3)
Bytecode Compilation & Marshalling: The Python source code of all stages is compiled into optimized bytecode (.pyc) and then marshaled. This removes readable strings and code structures, defeating simple static analysis.
Hybrid Encryption Scheme:
Final Payload (Stage 3): Compressed with zlib and encrypted with a strong, one-time AES-256 key.
Intermediate Loader (Stage 2): Encrypted with a custom, deterministic stream cipher (SimpleStreamCipher).
Hardware-Bound Keying: The decryption key for Stage 2 is dynamically generated at runtime based on a unique hardware fingerprint of the target machine (MAC address, CPU architecture, platform info). This makes the loader inert and non-functional in most sandboxes and analysis environments.
Advanced Anti-Analysis: The loader actively checks for signs of being analyzed before execution:
Anti-Debugging: Detects if a debugger is attached (sys.gettrace).
Anti-VM/Sandbox: Checks for common sandbox characteristics like low CPU count and lack of user activity (mouse movement).
In-Memory Execution: The entire decryption and execution chain occurs entirely in memory. The original payload is never written to disk, minimizing the forensic footprint.
Python 2/3 Compatibility: The generated loader contains logic to handle differences between Python 2 and 3 (specifically the exec statement/function), increasing its portability.
How It Bypasses Security Measures
Nyx is designed to counter two primary forms of security analysis:

1. Bypassing Static Analysis (Antivirus Scanners)
Static analysis involves scanning files for known malicious signatures without executing them. Nyx defeats this by:

Encrypting the Payload: The core malicious code is encrypted and packed multiple times. Its signature is not present in the final loader file.
Polymorphism: Since each build randomizes internal names, no two loaders have the same hash or signature.
Bytecode Obfuscation: By converting all code to marshaled bytecode, the loader avoids cleartext indicators that scanners look for.
2. Bypassing Dynamic Analysis (EDRs, Sandboxes)
Dynamic analysis involves running the file in a controlled environment to observe its behavior. Nyx defeats this by:

Environment Checks: The anti-analysis routines detect the artificial environment of a sandbox and cause the loader to exit silently before any malicious behavior is exhibited. The sandbox will report that the program did nothing harmful.
Hardware-Bound Decryption: This is the most powerful evasion feature. Since the decryption key for the second stage is tied to the target's hardware, the payload will fail to decrypt in a sandbox with a different hardware profile, causing a silent crash.
Fileless Execution: By operating entirely in memory, it avoids triggering alerts based on file creation or modification on disk, a common focus for EDRs.
Supported Payloads
Currently, Nyx is designed to encrypt and pack Python (.py) scripts.

While the core engine is Python-specific, the principles of multi-stage loading and in-memory execution can be adapted for other types of payloads. However, in its current form, it does not support binary executables (.exe), DLLs, or shellcode directly.

Installation
You need Python 3.6+ and the following library to run nyx_builder.py:
    pip install pycryptodomex
The generated loader.py also requires pycryptodomex to be installed on the target machine.

Usage
Configuration and usage are simple and straightforward.

Prepare your payload: Place your final Python script in the same directory and name it payload.py.
Configure the builder (optional): Open nyx_builder.py and modify the SOURCE_FILE and OUTPUT_FILE variables at the top if you wish to use different names.
Run the builder:
  python nyx_builder.py
Deploy: The script will generate the packed_loader.py file (or the name you specified), which is now ready to be deployed.

