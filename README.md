Nyx is an advanced, polymorphic, multi-stage crypter for Python, designed for educational purposes in the fields of malware analysis, reverse engineering, and defensive security research. It transforms a standard Python script into a stealthy, multi-layered loader engineered to evade detection by both static and dynamic analysis tools.

Disclaimer: This tool is intended for academic and research purposes only. The author is not responsible for any misuse or damage caused by this program. Unauthorized use of this tool on systems you do not own is illegal.

Features
Nyx employs a sophisticated, layered approach to conceal and execute Python payloads, making it a powerful tool for understanding modern evasion techniques.

Polymorphic Code Generation: Each build produces a loader with a unique signature. Variable and function names are randomized, rendering signature-based detection ineffective.
Multi-Stage Execution: The payload is executed through a chain of in-memory loaders. The initial loader (Stage 1) only contains logic to decrypt the next stage, keeping the final payload deeply hidden.
Loader (Stage 1) -> AES Decryptor (Stage 2) -> Final Payload (Stage 3)
Bytecode Compilation & Marshalling: The Python source code is compiled into optimized bytecode (.pyc) and then marshaled. This removes readable strings and code structures, defeating simple static analysis.
Hybrid Encryption Scheme:
Final Payload (Stage 3): Encrypted with a strong, one-time AES-256 key.
Intermediate Loader (Stage 2): Encrypted with a custom, deterministic stream cipher.
Hardware-Bound Keying: The decryption key for Stage 2 is dynamically generated at runtime based on a unique hardware fingerprint of the target machine (MAC address, CPU architecture, etc.). This makes the loader inert and non-functional in most sandboxes and analysis environments.
Advanced Anti-Analysis: The loader actively checks for signs of being analyzed:
Anti-Debugging: Detects if a debugger is attached (sys.gettrace).
Anti-VM/Sandbox: Checks for common sandbox characteristics like low CPU count and lack of user activity (mouse movement).
In-Memory Execution: The entire decryption and execution chain occurs entirely in memory. The original payload is never written to disk, minimizing forensic footprint.
Professional CLI: A clean command-line interface powered by argparse for ease of use, including a detailed help menu.
How It Bypasses Security Measures
Nyx is designed to counter two primary forms of security analysis:

1. Bypassing Static Analysis (Antivirus Scanners)
Static analysis involves scanning files for known malicious signatures without executing them. Nyx defeats this by:

Encrypting the Payload: The core malicious code is encrypted, so its signature is not present in the loader file.
Polymorphism: Since each build is structurally unique, no two loaders have the same hash or signature.
Hiding Imports and Strings: All sensitive code is converted to bytecode, removing cleartext indicators that scanners look for.
2. Bypassing Dynamic Analysis (EDRs, Sandboxes)
Dynamic analysis involves running the file in a controlled environment to observe its behavior. Nyx defeats this by:

Environment Checks: The anti-analysis routines detect the artificial environment of a sandbox and cause the loader to exit silently before any malicious behavior is exhibited.
Hardware-Bound Decryption: This is the most powerful evasion feature. Since the decryption key is tied to the target's hardware, the payload will fail to decrypt in a sandbox with a different hardware profile. The sandbox will report that the program did nothing harmful.
Fileless Execution: By operating entirely in memory, it avoids triggering alerts based on file creation or modification on disk, a common focus for EDRs.
Supported Payloads
Currently, Nyx is designed to encrypt and pack Python (.py) scripts.

While the core engine is Python-specific, the principles of multi-stage loading and in-memory execution can be adapted for other types of payloads. However, in its current form, it does not support binary 

Installation
You need Python 3.6+ and the following library:

pip install pycryptodomex


Usage
Nyx is operated via the command line.

Basic Usage
This will encrypt your_payload.py and create a loader named packed_loader.py.

python nyx_builder.py your_payload.py

Specifying an Output File
Use the -o or --output flag to name the output file.

python nyx_builder.py your_payload.py -o my_app.py

Getting Help
For a full list of commands and options, use the --help flag.

python nyx_builder.py --help

usage: nyx_builder.py [-h] [-o OUTPUT] source

Nyx Builder: An advanced polymorphic crypter for Python.

positional arguments:
  source                Path to the Python payload script to be packed.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path for the generated output loader file.
                        (default: packed_loader.py)

Example: python nyx_builder.py sensitive_script.py -o loader.py



executables (.exe), DLLs, or shellcode directly.

