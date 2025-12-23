import uuid
import pytest

from bot.utils.callbacks import pack_uuid, unpack_uuid


def test_pack_uuid_returns_string():
    u = str(uuid.uuid4())
    packed = pack_uuid(u)

    assert isinstance(packed, str)


def test_pack_unpack_uuid_roundtrip():
    original = str(uuid.uuid4())

    packed = pack_uuid(original)
    unpacked = unpack_uuid(packed)

    assert unpacked == original


def test_unpack_uuid_invalid_string():
    with pytest.raises(Exception):
        unpack_uuid("invalid-uuid-string")
