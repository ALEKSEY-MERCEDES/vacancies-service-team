# bot/utils/callbacks.py
import base64
import uuid


def pack_uuid(u: str) -> str:
    """
    UUID (36 символов) -> короткая urlsafe base64 строка (~22 символа)
    """
    b = uuid.UUID(str(u)).bytes
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")


def unpack_uuid(s: str) -> str:
    """
    короткая строка (~22) -> UUID строкой (36)
    """
    padding = "=" * (-len(s) % 4)
    b = base64.urlsafe_b64decode(s + padding)
    return str(uuid.UUID(bytes=b))
