import base64
import hashlib
import json
from Crypto.Cipher import AES
from datetime import datetime
from Crypto.Util.Padding import unpad

config_keys = [
    "662ede816988e58fb6d057d9d85605e0",
    "162exe235948e37ws6d057d9d85324e2",
    "962exe865948e37ws6d057d4d85604e0",
    "175exe868648e37wb9x157d4l45604l0",
    "175exe867948e37wb9d057d4k45604l0"
]

def decrypt(encrypted_content, hide_mes=False):
    decrypted_data = None
    try:
        config_file = json.loads(encrypted_content)
        parts = config_file['d'].split('.')
        iv = parts[1]
        data = parts[0]

        key = md5crypt(config_keys[1] + " " + str(config_file['v']))
        secret_key_spec = key.encode('utf-8')
        iv_parameter_spec = base64.b64decode(iv)

        cipher = AES.new(secret_key_spec, AES.MODE_CBC, iv_parameter_spec)
        decrypted_bytes = unpad(cipher.decrypt(base64.b64decode(data)), AES.block_size)
        decrypted_data = decrypted_bytes.decode('utf-8')

        decrypted_data = parse_config(json.loads(decrypted_data), hide_mes)
    except Exception as e:
        print(f"Decryption failed! Error: {e}")

    return decrypted_data

def parse_config(data, hide_mes):
    result_builder = []
    result_builder.append(f"[</>] [SSH Server] {data.get('sshServer')}")
    result_builder.append(f"[</>] [SSH Port] {data.get('sshPort')}")

    ssh_auth = data.get('profileSshAuth')
    if ssh_auth:
        result_builder.append(f"[</>] [SSH Username] {ssh_auth.get('sshUser')}")
        if 'sshPasswd' in ssh_auth:
            result_builder.append(f"[</>] [SSH Password] {ssh_auth.get('sshPasswd')}")

    result_builder.append(f"[</>] [Enable data compression] {data.get('enableDataCompression', False)}")
    result_builder.append(f"[</>] [Disable TCP Delay] {data.get('disableTcpDelay', False)}")
    proxy_type = data.get('proxyType', 'SSH DIRECT')
    result_builder.append(f"[</>] [Connection type] {proxy_type}")

    if proxy_type.startswith("PROXY_HTTP"):
        proxy_http = data.get('proxyHttp')
        if proxy_http:
            result_builder.append(f"[</>] [Proxy Host] {proxy_http.get('proxyIp')}")
            result_builder.append(f"[</>] [Proxy Port] {proxy_http.get('proxyPort')}")
            result_builder.append(f"[</>] [Use custom payload for proxy] {proxy_http.get('isCustomPayload')}")
            result_builder.append(f"[</>] [Proxy Payload] {proxy_http.get('customPayload')}")

    if proxy_type == "PROXY_SSL":
        proxy_ssl = data.get('proxySsl')
        if proxy_ssl:
            result_builder.append(f"[</>] [SSL/SNI Value] {proxy_ssl.get('hostSni')}")
            result_builder.append(f"[</>] [SSL Version] {proxy_ssl.get('versionSSl')}")
            result_builder.append(f"[</>] [Use custom payload for SSL] {proxy_ssl.get('isSSLCustomPayload')}")
            result_builder.append(f"[</>] [SSL Payload] {proxy_ssl.get('customPayloadSSL')}")

    if proxy_type == "SSH DIRECT":
        proxy_direct = data.get('proxyDirect')
        if proxy_direct:
            result_builder.append(f"[</>] [Use custom payload] {proxy_direct.get('isCustomPayload')}")
            result_builder.append(f"[</>] [SSH Direct Payload] {proxy_direct.get('customPayload')}")

    result_builder.append(f"[</>] [Custom DNS Servers] {data.get('dnsCustom')}")
    config_protect = data.get('configProtect')
    if config_protect:
        result_builder.append(f"[</>] [Block config] {config_protect.get('blockConfig')}")
        validity = config_protect.get('validity')
        expire_date = datetime.fromtimestamp(validity).strftime('%Y-%m-%d %H:%M:%S') if validity and validity > 0 else 'N/A'
        result_builder.append(f"[</>] [Expire Date] {expire_date}")
        result_builder.append(f"[</>] [Block rooted devices] {config_protect.get('blockRoot')}")
        result_builder.append(f"[</>] [Block non-PlayStore app] {config_protect.get('blockAuthEdition')}")
        result_builder.append(f"[</>] [Use only mobile data] {config_protect.get('onlyMobileData')}")
        result_builder.append(f"[</>] [Enable HWID] {config_protect.get('blockByPhoneId')}")
        result_builder.append(f"[</>] [HWID Value] {config_protect.get('phoneId')}")
        result_builder.append(f"[</>] [Hide SSH Server Message] {config_protect.get('hideMessageServer')}")
        if not hide_mes and 'message' in config_protect:
            result_builder.append(f"[</>] [Message] {config_protect.get('message')}")

    result_builder.append("\n============== Configuration ==============\n")
    result_builder.append("[</>] [Made By] Biar")

    return "\n".join(result_builder)

def md5crypt(data):
    digest = hashlib.md5(data.encode('utf-8')).hexdigest()
    return digest

def file_sockshttp(file_content):
    hide_mes = False
    decrypted_data = decrypt(file_content, hide_mes)
    return(decrypted_data)