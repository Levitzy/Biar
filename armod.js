const CryptoJS = require('crypto-js');
const base64 = require('base-64');

const ENCRYPTION_KEY = "YXJ0dW5uZWw3ODc5Nzg5eA==";

function decryptConfig(encryptedConfig) {
    const key = CryptoJS.enc.Base64.parse(ENCRYPTION_KEY);
    const cipherParams = CryptoJS.lib.CipherParams.create({
        ciphertext: CryptoJS.enc.Base64.parse(encryptedConfig)
    });
    const decrypted = CryptoJS.AES.decrypt(cipherParams, key, {
        mode: CryptoJS.mode.ECB,
        padding: CryptoJS.pad.Pkcs7
    });
    return decrypted.toString(CryptoJS.enc.Utf8);
}

function processConfig(config) {
    const patternVmess = /^ar-(vmess):\/\//;
    const patternSsh = /^ar-(ssh|vless|socks|trojan-go|trojan|ssr):\/\//;

    const matcherVmess = config.match(patternVmess);
    const matcherSsh = config.match(patternSsh);

    if (matcherVmess) {
        const encryptedConfig = config.slice(matcherVmess[0].length);
        const decryptedConfig = decryptConfig(encryptedConfig);
        const decodedConfig = decodeURIComponent(decryptedConfig);
        return formatDecryptionResult("VMess", decodedConfig);
    } else if (matcherSsh) {
        const encryptedConfig = config.slice(matcherSsh[0].length);
        const decryptedConfig = decryptConfig(encryptedConfig);
        let decodedConfig = decodeURIComponent(decryptedConfig);
        decodedConfig = replaceNeedlessCharacters(decodedConfig);
        return formatDecryptionResult("SSH", decodedConfig);
    } else {
        return "Invalid config or unlock config";
    }
}

function formatDecryptionResult(configType, decryptedConfig) {
    return `Decrypted ${configType} Config:\n${decryptedConfig}`;
}

function replaceNeedlessCharacters(text) {
    return text.replace(/&/g, "\n").replace(/\?/g, "\n");
}

// Example usage:
const encryptedConfig = "your_encrypted_config_here";
console.log(processConfig(encryptedConfig));
