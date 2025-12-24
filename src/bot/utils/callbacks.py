# bot/utils/callbacks.py
import base64
import uuid


def pack_uuid(u: str) -> str:
    b = uuid.UUID(str(u)).bytes
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")


def unpack_uuid(s: str) -> str:
    """
    Принимает:
      - short base64 (~22 символа)
      - обычный uuid строкой (36 символов)
    Возвращает uuid строкой (36).
    """
    s = (s or "").strip()

    # 1) уже UUID
    try:
        return str(uuid.UUID(s))
    except Exception:
        pass

    # 2) short base64
    try:
        padding = "=" * (-len(s) % 4)
        b = base64.urlsafe_b64decode(s + padding)
        if len(b) != 16:
            raise ValueError(f"decoded bytes len={len(b)} (expected 16)")
        return str(uuid.UUID(bytes=b))
    except Exception as e:
        raise ValueError(f"Bad uuid token: {s}") from e