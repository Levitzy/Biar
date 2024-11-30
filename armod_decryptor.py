import base64
from Crypto.Cipher import AES
import json
import re
from urllib.parse import unquote

ENCRYPTION_KEY = "YXJ0dW5uZWw3ODc5Nzg5eA=="

def decrypt_config(encrypted_config):
    key = base64.b64decode(ENCRYPTION_KEY)
    cipher = AES.new(key, AES.MODE_ECB)
    decoded_value = base64.b64decode(encrypted_config)
    decrypted_value = cipher.decrypt(decoded_value)
    return decrypted_value.decode('utf-8')

def process_config(config):
    pattern_vmess = "^ar-(vmess)://"
    pattern_ssh = "^ar-(ssh|vless|socks|trojan-go|trojan|ssr)://"

    matcher_vmess = re.search(pattern_vmess, config)
    matcher_ssh = re.search(pattern_ssh, config)

    if matcher_vmess:
        encrypted_config = config[matcher_vmess.end():]
        decrypted_config = decrypt_config(encrypted_config)
        decoded_config = unquote(decrypted_config)
        return format_decryption_result("VMess", decoded_config)
    elif matcher_ssh:
        encrypted_config = config[matcher_ssh.end():]
        decrypted_config = decrypt_config(encrypted_config)
        decoded_config = unquote(decrypted_config)
        decoded_config = replace_needless_characters(decoded_config)
        return format_decryption_result("SSH", decoded_config)
    else:
        return "Invalid config or unlock config"

def format_decryption_result(config_type, decrypted_config):
    return f"Decrypted {config_type} Config:\n{decrypted_config}"

def replace_needless_characters(text):
    return text.replace("&", "\n").replace("?", "\n")
