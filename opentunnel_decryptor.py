import base64
import re
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def decrypt(encrypted_content: str) -> str:
    arr_content = encrypted_content.split('.')
    salt = base64.b64decode(arr_content[0].strip())
    nonce = base64.b64decode(arr_content[1].strip())
    cipher = base64.b64decode(arr_content[2].strip())
    
    cipher_text = cipher[:-16]
    config_enc_password = "B1m93p$$9pZcL9yBs0b$jJwtPM5VG@Vg"
    
    pbkdf2_key = pbkdf2_key_gen(config_enc_password, salt, 1000, 16)
    if pbkdf2_key is None:
        return "Failed to generate PBKDF2 key."
    
    decrypted_result = aes_decrypt(cipher, pbkdf2_key, nonce)
    if decrypted_result is None:
        return "Failed to decrypt AES."
    
    unpadded_result = remove_padding(decrypted_result)
    decrypted_string = unpadded_result.decode('utf-8')
    pattern = re.compile(r'<entry key="(.*?)">(.*?)</entry>')
    matcher = pattern.finditer(decrypted_string)
    
    result_builder = ["\n"]
    for match in matcher:
        key = match.group(1)
        value = match.group(2)
        result_builder.append(f"[</>] [{key}]= {value}\n")
    result_builder.append("\n")
    return ''.join(result_builder)

def pbkdf2_key_gen(password: str, salt: bytes, count: int, dk_len: int) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=dk_len,
        salt=salt,
        iterations=count,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def aes_decrypt(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
    try:
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        print(f"Error during decryption: {e}")
        return None

def remove_padding(decrypted_text: bytes) -> bytes:
    padding_length = decrypted_text[-1]
    return decrypted_text[:-padding_length]

def b64decode(content: str) -> bytes:
    return base64.b64decode(content)

def tnl_decryptor(file_content):
    decrypted_content = decrypt(file_content)
    return(decrypted_content)
