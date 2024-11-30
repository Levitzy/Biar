import base64
from Crypto.Cipher import AES
import json
import re

KEY = "X25ldHN5bmFfbmV0bW9kXw=="

def decrypt(encrypted_data):
    try:
        key_bytes = base64.b64decode(KEY)
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        decrypted_string = decrypted_bytes.decode('utf-8').strip()
        return format_decrypted_data(decrypted_string)
    except Exception as e:
        return f"Error during decryption: {e}"

def format_decrypted_data(decrypted_data):
    formatted_data = []
    try:
        # Attempt to parse the entire string as a single JSON object
        json_data = json.loads(decrypted_data)
        formatted_data.append(format_json(json_data))
    except json.JSONDecodeError:
        # If that fails, attempt to find and parse multiple JSON objects within the string
        json_objects = find_json_objects(decrypted_data)
        if not json_objects:
            formatted_data.append("No valid JSON objects found.")
        for i, obj in enumerate(json_objects):
            try:
                json_data = json.loads(obj)
                formatted_data.append(format_json(json_data))
            except json.JSONDecodeError as e:
                formatted_data.append(f"Error parsing JSON data in object {i + 1}: {e}")
    return "\n\n".join(formatted_data)

def find_json_objects(text):
    """
    This function uses a regular expression to find JSON objects in a string.
    It matches braces to extract JSON objects.
    """
    json_objects = []
    brace_count = 0
    start_index = 0
    in_string = False

    for i, char in enumerate(text):
        if char == '"' and (i == 0 or text[i - 1] != '\\'):
            in_string = not in_string
        if not in_string:
            if char == '{':
                if brace_count == 0:
                    start_index = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_objects.append(text[start_index:i + 1])

    return json_objects

def format_json(data):
    """
    Custom format the JSON data as per the provided example without space indent.
    """
    result = []
    def recurse(obj, prefix=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    result.append(f"{prefix}[</>] [{key}]:")
                    recurse(value, prefix)
                else:
                    result.append(f"{prefix}[</>] [{key}]: {value}")
        elif isinstance(obj, list):
            for item in obj:
                recurse(item, prefix)
    recurse(data)
    return "\n".join(result)

def decrypt_file(file_content):
    return decrypt(file_content)
