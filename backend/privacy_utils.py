try:
    import keyring
except ImportError:
    keyring = None

from cryptography.fernet import Fernet
import os
import base64

class SovereignVault:
    SERVICE_NAME = "akasha_sovereign_vault"
    KEY_NAME = "master_key"
    FALLBACK_PATH = os.path.join(os.path.dirname(__file__), "akasha_data", "sovereign_vault", "master.key")

    def __init__(self):
        self._key = self._get_or_create_key()
        self._fernet = Fernet(self._key)

    def _get_or_create_key(self):
        key = None
        
        # Try Keyring first
        if keyring:
            try:
                key = keyring.get_password(self.SERVICE_NAME, self.KEY_NAME)
            except Exception:
                key = None
                
        # Fallback to local file if keyring failed or not available
        if not key:
            if os.path.exists(self.FALLBACK_PATH):
                with open(self.FALLBACK_PATH, "r") as f:
                    key = f.read().strip()
            else:
                # Generate new key
                key = Fernet.generate_key().decode('utf-8')
                os.makedirs(os.path.dirname(self.FALLBACK_PATH), exist_ok=True)
                with open(self.FALLBACK_PATH, "w") as f:
                    f.write(key)
                    
        return key.encode('utf-8')

    def encrypt(self, data: str) -> str:
        if not data:
            return data
        return self._fernet.encrypt(data.encode('utf-8')).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> str:
        if not encrypted_data:
            return encrypted_data
        try:
            return self._fernet.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
        except Exception:
            # If decryption fails, return as is (maybe it wasn't encrypted or key changed)
            return encrypted_data

vault = SovereignVault()
