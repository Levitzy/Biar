from flask import Flask, request, jsonify
import base64
import re
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from urllib.parse import unquote_plus

app = Flask(__name__)

def decrypt(encrypted_content: str) -> str:
    try:
        arr_content = encrypted_content.split('.')
        salt = base64.b64decode(arr_content[0].strip())
        nonce = base64.b64decode(arr_content[1].strip())
        ciphertext = base64.b64decode(arr_content[2].strip())

        config_enc_password = "B1m93p$$9pZcL9yBs0b$jJwtPM5VG@Vg"  # In real-world app, store this securely

        pbkdf2_key = pbkdf2_key_gen(config_enc_password, salt, 1000, 16)
        if pbkdf2_key is None:
            return "Failed to generate PBKDF2 key."

        decrypted_result = aes_decrypt(ciphertext, pbkdf2_key, nonce)
        if decrypted_result is None:
            return "Failed to decrypt AES."

        unpadded_result = remove_padding(decrypted_result)
        decrypted_string = unpadded_result.decode('utf-8')
        pattern = re.compile(r'<entry key="(.*?)">(.*?)</entry>')
        matcher = pattern.finditer(decrypted_string)

        result = {}
        for match in matcher:
            key = match.group(1)
            value = match.group(2)
            result[key] = value

        return result

    except Exception as e:
        print(f"Error during decryption: {e}")
        return None

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

@app.route('/decrypt', methods=['GET'])
def decrypt_route():
    try:
        encrypted_content = request.args.get('content')
        if not encrypted_content:
            return jsonify({'status': 'error', 'message': 'Missing encrypted content'}), 400

        decoded_content = unquote_plus(encrypted_content)
        result = decrypt(decoded_content)

        if result is None:
            return jsonify({'status': 'error', 'message': 'Decryption failed'}), 500

        return jsonify({'status': 'success', 'decrypted_content': result}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)  # In production, use a proper WSGI server like Gunicorn