import hashlib
import secrets


def generate_device_key():
  return secrets.token_urlsafe(32)


def hash_device_key(device_key:str):
  return hashlib.sha256(
    device_key.encode("utf-8")
  ).hexdigest()