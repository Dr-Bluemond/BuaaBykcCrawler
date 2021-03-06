import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, padding, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
import random

# 这是一个1024bit的RSA公钥
RSA_PUBLIC_KEY = b"MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDlHMQ3B5GsWnCe7Nlo1YiG/YmHdlOiKOST5aRm4iaqYSvhvWmwcigoyWTM+8bv2+sf6nQBRDWTY4KmNV7DBk1eDnTIQo6ENA31k5/tYCLEXgjPbEjCK9spiyB62fCT6cqOhbamJB0lcDJRO6Vo1m3dy+fD0jbxfDVBBNtyltIsDQIDAQAB"

# 需要首先用base64解码，然后再用der来load
public_key = serialization.load_der_public_key(base64.b64decode(RSA_PUBLIC_KEY), backend=default_backend())


def generate_aes_key() -> bytes:
    return "".join(
        [random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(16)]
    ).encode()


# aes加密用的ECB模式，padding用的pkcs
# JavaScript源码中声明iv等于key，但是搞笑的是ECB模式并不需要iv，科技公司需要提高自己的密码学水平
def aes_encrypt(message: bytes, key: bytes) -> bytes:
    padder = padding.PKCS7(128).padder()
    padded_message = padder.update(message) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()

    encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
    return encrypted_message


def aes_decrypt(message: bytes, key: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_message = decryptor.update(message) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    unpadded_message = unpadder.update(decrypted_message) + unpadder.finalize()
    return unpadded_message


def sign(message: bytes) -> bytes:
    digist = hashes.Hash(hashes.SHA1(), backend=default_backend())
    digist.update(message)
    return base64.b16encode(digist.finalize()).lower()


def rsa_encrypt(message: bytes) -> bytes:
    encrypted = public_key.encrypt(message, asymmetric_padding.PKCS1v15())
    return base64.b64encode(encrypted)
