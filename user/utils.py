import hashlib


def Encrypt(value):
    return hashlib.sha256(value.encode()).hexdigest()


def VerifyToken(hashed, value):
    return True if hashed == Encrypt(value) else False
