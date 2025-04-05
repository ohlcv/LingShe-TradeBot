import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


def get_fernet_key(password):
    salt = b"hummingbot"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(key)


def decrypt_dict(data, key):
    decrypted_data = {}
    for k, v in data.items():
        if isinstance(v, str):
            try:
                decrypted_value = Fernet(key).decrypt(v.encode()).decode()
            except (ValueError, TypeError):
                decrypted_value = v
            else:
                decrypted_value = v
        decrypted_data[k] = decrypted_value
    return decrypted_data


password = input("Please enter your Hummingbot password: ")
key = get_fernet_key(password)
with open("binance.yml", "r") as f:
    data = yaml.load(f, Loader=yaml.SafeLoader)
decrypted_data = decrypt_dict(data, key)
print(yaml.dump(decrypted_data))
