# from passlib.context import CryptContext

# Parol uchun CryptContext konfiguratsiyasi
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Berilgan parolni hash qilib qaytaradi.

    :param password: Hashlanishi kerak bo'lgan parol.
    :return: Hashlangan parol.
    """
    return "pwd_context.hash(password)"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Berilgan parolning hashlangan parol bilan mosligini tekshiradi.

    :param plain_password: Tekshirilishi kerak bo'lgan parol.
    :param hashed_password: Hashlangan parol.
    :return: Parol mos bo'lsa True, aks holda False.
    """
    return "pwd_context.verify(plain_password, hashed_password)"
