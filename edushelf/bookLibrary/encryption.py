from cryptography.fernet import Fernet
from django.conf import settings
import base64

KEY = getattr(settings, "ENCRYPTION_KEY", None)
if not KEY:
    raise ValueError("ENCRYPTION_KEY не установлен в settings!")

CIPHER_SUITE = Fernet(KEY)

def encrypt_email(email: str) -> str:
    return CIPHER_SUITE.encrypt(email.encode()).decode()

def decrypt_email(encrypted_email: str) -> str:
    return CIPHER_SUITE.decrypt(encrypted_email.encode()).decode()
