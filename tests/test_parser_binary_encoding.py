"""Unit tests for pkl.parser.Parser against the pkl-binary wire encoding.

These exercise the decoder directly against hand-built MessagePack-style
arrays (as documented in bindings-specification/binary-encoding.adoc), so
they don't need a real `pkl` binary/subprocess.
"""

from pkl.parser import CODE_BYTES, CODE_DURATION, Parser


def test_bytes_decodes_to_python_bytes():
    """`Bytes` (type code 0x0F) added in Pkl 0.29; wire encoding documented
    as [0x0F, <bin>]. Previously unhandled, so the parser silently returned
    {"type": "Unknown", "value": obj} instead of the actual bytes.
    """
    parser = Parser()
    obj = [CODE_BYTES, b"\x01\x02\x03"]

    result = parser.handle_type(obj)

    assert result == b"\x01\x02\x03"
    assert isinstance(result, bytes)


def test_decoder_ignores_unknown_trailing_slots():
    """Pkl 0.30's binary-encoding.adoc formalizes forward compatibility:
    "Additional slots may be added to types in future Pkl releases.
    Decoders *must* be designed to defensively discard values beyond the
    number of known slots for a type[...]".

    Fixed-arity unpacking (`_, value, unit = obj`) would raise
    "too many values to unpack" on a future Pkl release that appends a
    slot; decoders must tolerate and ignore extras instead.
    """
    parser = Parser()
    obj = [CODE_DURATION, 5.0, "s", "some-future-slot"]

    result = parser.handle_type(obj)

    assert result.value == 5.0
    assert result.unit == "s"
