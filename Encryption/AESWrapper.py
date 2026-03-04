from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class AESWrapper:

    @staticmethod
    def generate_key(n=32, password="", salt=b"") -> bytes:
        if salt == b"":
            salt = get_random_bytes(n)
        key = PBKDF2(password, salt, dkLen=n)
        return key

    @staticmethod
    def encrypt(key: bytes, msg: bytes) -> bytes:
        cipher = AES.new(key, AES.MODE_GCM)
        data = cipher.encrypt(pad(msg, AES.block_size))
        return cipher.nonce + data

    @staticmethod
    def decrypt(key: bytes, ciphertext: bytes) -> bytes:
        nonce = ciphertext[:16]
        ciphertext = ciphertext[16:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        msg = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return msg