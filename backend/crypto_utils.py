import os
from cryptography.fernet import Fernet


class CryptoUtils:
    def __init__(self):
        key = os.getenv("CHAT_ENCRYPTION_KEY")
        if not key:
            raise ValueError("CHAT_ENCRYPTION_KEY nao definida no .env")
        self._fernet = Fernet(key.encode())

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode()).decode()
