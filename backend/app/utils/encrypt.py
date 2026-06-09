"""密码加密解密工具"""
import base64
import hashlib
from cryptography.fernet import Fernet
from config.settings import settings


def _get_key() -> bytes:
    """从配置密钥生成 Fernet key"""
    key = hashlib.sha256(settings.ENCRYPT_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt(plain_text: str) -> str:
    """加密明文"""
    if not plain_text:
        return ""
    f = Fernet(_get_key())
    return f.encrypt(plain_text.encode()).decode()


def decrypt(cipher_text: str) -> str:
    """解密密文"""
    if not cipher_text:
        return ""
    try:
        f = Fernet(_get_key())
        return f.decrypt(cipher_text.encode()).decode()
    except Exception:
        return cipher_text  # 兼容未加密的旧数据
