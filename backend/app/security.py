import secrets

from argon2 import PasswordHasher

password_hasher = PasswordHasher()


def generate_share_id() -> str:
    return secrets.token_urlsafe(16)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)
