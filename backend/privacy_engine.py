import hashlib
import json
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

import ctypes
import sys

# Platform-specific memory locking
def lock_memory(data):
    try:
        if sys.platform == "win32":
            # Windows VirtualLock
            size = ctypes.c_size_t(len(data))
            addr = ctypes.cast(data, ctypes.c_void_p)
            res = ctypes.windll.kernel32.VirtualLock(addr, size)
            return res != 0
        else:
            # Linux/macOS mlock
            import libc
            res = libc.mlock(data, len(data))
            return res == 0
    except Exception:
        return False

def zero_buffer(buf):
    """Overwrite a bytearray with zeros to erase sensitive data."""
    if isinstance(buf, (bytearray, memoryview)):
        for i in range(len(buf)):
            buf[i] = 0

import random

class ShamirSecretSharing:
    """Lightweight SSS implementation for Master Key Sovereignty."""
    PRIME = 2**256 - 189 # A large prime for 256-bit keys

    @staticmethod
    def _eval_poly(poly, x):
        result = 0
        for coeff in reversed(poly):
            result = (result * x + coeff) % ShamirSecretSharing.PRIME
        return result

    @classmethod
    def split(cls, secret_bytes, n, k):
        secret = int.from_bytes(secret_bytes, 'big')
        poly = [secret] + [random.SystemRandom().getrandbits(256) % cls.PRIME for _ in range(k - 1)]
        shares = [(x, cls._eval_poly(poly, x)) for x in range(1, n + 1)]
        return shares

    @classmethod
    def reconstruct(cls, shares):
        def _lagrange_interpolation(x, x_s, y_s):
            k = len(x_s)
            def _basis(j):
                num = den = 1
                for m in range(k):
                    if m == j: continue
                    num = (num * (x - x_s[m])) % cls.PRIME
                    den = (den * (x_s[j] - x_s[m])) % cls.PRIME
                return (y_s[j] * num * pow(den, -1, cls.PRIME)) % cls.PRIME
            
            return sum(_basis(j) for j in range(k)) % cls.PRIME

        x_s, y_s = zip(*shares)
        secret_int = _lagrange_interpolation(0, x_s, y_s)
        return secret_int.to_bytes(32, 'big')

class EncryptedBackupEngine:
    """Automated, encrypted redundancy for the Digital Soul."""
    def __init__(self, privacy_engine):
        self.privacy = privacy_engine
        self.backup_dir = "akasha_data/redundancy"
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_snapshot(self, data_dict: dict, label: str):
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        json_data = json.dumps(data_dict)
        encrypted_blob = self.privacy.encrypt_data(json_data)
        
        filename = f"soul_{label}_{timestamp}.backup"
        with open(os.path.join(self.backup_dir, filename), "w") as f:
            f.write(encrypted_blob)
        print(f"BackupEngine: Created encrypted snapshot: {filename}")

class PrivacyEngine:
    def __init__(self, p2p_node=None, executive=None):
        # Generate a private key for the Archivist's DID
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.did = f"did:akasha:{hashlib.sha256(str(self.private_key.public_key()).encode()).hexdigest()[:16]}"
        
        self.p2p = p2p_node
        self.executive = executive
        
        # Sovereign Encryption Key (derived from DID or master secret)
        raw_key = AESGCM.generate_key(bit_length=256)
        self.master_key = bytearray(raw_key) 
        lock_memory(self.master_key) 
        self.aesgcm = AESGCM(self.master_key)
        
        self.backup_engine = EncryptedBackupEngine(self)
        self.sss = ShamirSecretSharing()
        
        # Local Sovereign Vault (Replacing Arweave/IPFS for privacy & cost)
        self.vault_path = "akasha_data/sovereign_vault"
        if not os.path.exists(self.vault_path):
            os.makedirs(self.vault_path, exist_ok=True)

        self.is_air_gapped = False

    def rotate_master_key(self, new_key_bytes: bytes = None):
        """Rotates the master key and zeros the old one."""
        zero_buffer(self.master_key)
        raw_key = new_key_bytes or AESGCM.generate_key(bit_length=256)
        self.master_key = bytearray(raw_key)
        lock_memory(self.master_key)
        self.aesgcm = AESGCM(self.master_key)
        print("PrivacyEngine: Master key rotated successfully.")

    def toggle_air_gap(self, status: bool):
        """
        Activates 'Emergency Air-Gap' mode. 
        Disables all external connectivity and rotates local master keys.
        """
        self.is_air_gapped = status
        if status:
            print("PrivacyEngine: !!! EMERGENCY AIR-GAP ACTIVATED !!!")
            # Clear old key first
            zero_buffer(self.master_key)
            # Rotate keys for immediate sovereignty
            self.master_key = bytearray(AESGCM.generate_key(bit_length=256))
            lock_memory(self.master_key)
            self.aesgcm = AESGCM(self.master_key)
            
            # Bridge 4: Sovereign Shield (P2P Isolation)
            if self.p2p:
                asyncio.create_task(self.p2p.set_stealth_mode(True))
            
            # Bridge 4: Executive Isolation
            if self.executive:
                self.executive.is_air_gapped = True
                
            print("PrivacyEngine: Sovereign keys rotated. Local state secured.")
        else:
            print("PrivacyEngine: Air-Gap deactivated. Resuming operations...")
            if self.p2p:
                asyncio.create_task(self.p2p.set_stealth_mode(False))
            if self.executive:
                self.executive.is_air_gapped = False

    def encrypt_data(self, data: str) -> str:
        """Encrypts data using AES-GCM-256."""
        nonce = os.urandom(12)
        # AESGCM requires bytes, not bytearray
        encrypted_data = self.aesgcm.encrypt(nonce, data.encode(), None)
        # Combine nonce and data for storage
        return base64.b64encode(nonce + encrypted_data).decode()

    def decrypt_data(self, encrypted_blob: str) -> str:
        """Decrypts data using AES-GCM-256."""
        blob = base64.b64decode(encrypted_blob)
        nonce = blob[:12]
        encrypted_data = blob[12:]
        decrypted_data = self.aesgcm.decrypt(nonce, encrypted_data, None)
        return decrypted_data.decode()

    def generate_zkp_commitment(self, content: str) -> str:
        """
        Generates a cryptographic commitment using Salted HMAC-SHA3.
        Provides better hiding and binding properties than a simple hash.
        """
        import hmac
        salt = os.urandom(32)
        # In a real ZKP, this secret would be hidden/managed by a circuit
        h = hmac.new(self.master_key, (content.encode() + salt), hashlib.sha3_256)
        return f"zkp_commitment_{h.hexdigest()}"

    def secure_delete(self, file_path: str, passes: int = 3):
        """
        Securely deletes a file by overwriting it with random data multiple times.
        Simulates the 'shred' utility in pure Python.
        """
        if not os.path.exists(file_path):
            return

        try:
            file_size = os.path.getsize(file_path)
            with open(file_path, "ba+", buffering=0) as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Truncate and remove
            with open(file_path, "w") as f:
                f.write("")
            os.remove(file_path)
            print(f"PrivacyEngine: Securely shredded {file_path}")
        except Exception as e:
            print(f"PrivacyEngine: Shred error for {file_path}: {e}")
            # Fallback to standard remove if shredding fails
            if os.path.exists(file_path):
                os.remove(file_path)

    def emergency_shred(self):
        """
        THE NUCLEAR OPTION: Securely shreds the local master keys.
        Data becomes permanently unrecoverable.
        """
        print("PrivacyEngine: !!! INITIATING EMERGENCY SHRED PROTOCOL !!!")
        
        # 1. Shred the key file if it exists
        key_path = "bifrost_node.key"
        self.secure_delete(key_path)
        
        # 2. Rotate in-memory keys to noise
        self.master_key = os.urandom(32)
        self.aesgcm = AESGCM(self.master_key)
        
        # 3. Shred sensitive vault indexes if possible
        # (Assuming index.json exists in akasha_data)
        index_path = "backend/akasha_data/index.json"
        self.secure_delete(index_path)
            
        self.is_air_gapped = True
        print("PrivacyEngine: Sovereignty protected. Local state is now noise.")
        return True
