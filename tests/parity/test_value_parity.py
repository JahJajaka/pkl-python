"""
Parity suite: decode a shared .pkl corpus through pkl-python and assert the
decoded Python values match pkl-go's documented behaviour / the Pkl binary-encoding
spec (https://pkl-lang.org/main/current/bindings-specification/binary-encoding.html),
since there is no reference pkl-go binary at test time (see tests/parity/README.md).

Uses pkl.load()'s default PreconfiguredOptions evaluator (not bare EvaluatorOptions())
so it doesn't trip the bare-options hang tracked in JAJ-824.

Fixtures under tests/_pkl/ are apple/pkl-go's own vendored test_fixtures (note the
`@go.Package` annotations) -- the most direct grounding available for "what pkl-go
does". tests/parity/fixtures/ adds the few value types not already covered there
(IntSeq, Regex, Bytes) plus a Dynamic example that avoids the mixed
element/property shape tests/_pkl/dynamic.pkl uses (which pkl-python's parser
rejects by design).
"""

import dataclasses
from pathlib import Path

import pytest

import pkl

PKL_GO_FIXTURES = Path(__file__).parent.parent / "_pkl"
FIXTURES = Path(__file__).parent / "fixtures"


def to_plain(value):
    """Recursively flatten dataclass instances (including pkl-python's dynamically
    generated Dynamic/Typed classes, which can't be imported to construct an
    `expected` instance of the same class) into plain dicts/lists/sets for
    structural comparison against a literal expected value.
    """
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            f.name: to_plain(getattr(value, f.name)) for f in dataclasses.fields(value)
        }
    if isinstance(value, list):
        return [to_plain(v) for v in value]
    if isinstance(value, dict):
        return {k: to_plain(v) for k, v in value.items()}
    if isinstance(value, set):
        return {to_plain(v) for v in value}
    return value


def test_to_plain_flattens_nested_dataclasses():
    """Local, non-subprocess sanity check for the to_plain() helper itself."""
    assert to_plain(pkl.Pair(1, pkl.Duration(2, "s"))) == {
        "first": 1,
        "second": {"value": 2, "unit": "s"},
    }
    assert to_plain([{"a", "b"}]) == [{"a", "b"}]


def test_primitives():
    config = pkl.load(PKL_GO_FIXTURES / "primitives.pkl")
    assert config.res0 == "bar"
    assert config.res1 == 1
    assert config.res2 == 2
    assert config.res3 == 3
    assert config.res4 == 4
    assert config.res5 == 5
    assert config.res6 == 6
    assert config.res7 == 7
    assert config.res8 == 8
    assert config.res9 == 5.3
    assert config.res10 is True
    assert config.res11 is None
    assert config.res12 == 33
    assert config.res13 == 33.3333


def test_duration():
    config = pkl.load(PKL_GO_FIXTURES / "duration.pkl")
    assert config.res1 == pkl.Duration(1, "ns")
    assert config.res2 == pkl.Duration(2, "us")
    assert config.res3 == pkl.Duration(3, "ms")
    assert config.res4 == pkl.Duration(4, "s")
    assert config.res5 == pkl.Duration(5, "min")
    assert config.res6 == pkl.Duration(6, "h")
    assert config.res7 == pkl.Duration(7, "d")
    assert config.res8 == "us"  # DurationUnit typealias resolves to a plain str


def test_datasize():
    config = pkl.load(PKL_GO_FIXTURES / "datasize.pkl")
    assert config.res1 == pkl.DataSize(1, "b")
    assert config.res2 == pkl.DataSize(2, "kb")
    assert config.res3 == pkl.DataSize(3, "mb")
    assert config.res4 == pkl.DataSize(4, "gb")
    assert config.res5 == pkl.DataSize(5, "tb")
    assert config.res6 == pkl.DataSize(6, "pb")
    assert config.res7 == pkl.DataSize(7, "kib")
    assert config.res8 == pkl.DataSize(8, "mib")
    assert config.res9 == pkl.DataSize(9, "gib")
    assert config.res10 == pkl.DataSize(10, "tib")
    assert config.res11 == pkl.DataSize(11, "pib")
    assert config.res12 == "mb"  # DataSizeUnit typealias resolves to a plain str


def test_collections():
    config = pkl.load(PKL_GO_FIXTURES / "collections.pkl")
    assert config.res1 == [1, 2, 3]  # List
    assert config.res2 == [2, 3, 4]  # Listing
    assert config.res3 == [[1], [2], [3]]  # List<List>
    assert config.res4 == [[1], [2], [3]]  # Listing<Listing>
    assert config.res5 == {1: True, 2: False}  # Mapping
    assert config.res6 == {1: {1: True}, 2: {2: True}, 3: {3: True}}
    assert config.res7 == {1: True, 2: False}  # Map
    assert config.res8 == {1: {1: True}, 2: {2: False}}
    assert config.res9 == {"one", "two", "three"}  # Set
    assert config.res10 == {1, 2, 3}
    assert config.res11 == pkl.Pair(1, 5.0)
    assert config.res12 == pkl.Pair("hello", "goodbye")
    assert config.res13 == pkl.Pair(1, 2)


def test_nullables():
    config = pkl.load(PKL_GO_FIXTURES / "nullables.pkl")
    assert config.res0 == "bar"
    assert config.res1 is None
    assert config.res2 == 1
    assert config.res3 is None
    assert config.res18 == 5.3
    assert config.res19 is None
    assert config.res20 is True
    assert config.res21 is None
    assert config.res22 == {"foo": "bar"}
    assert config.res23 is None
    assert config.res25 is None
    assert config.res26 == [1, 2, None, 4, 5]
    assert config.res27 is None
    assert to_plain(config.res28) == {"prop": None}
    assert to_plain(config.res29) == {"prop": "foo"}
    assert config.res30 is None


def test_unions():
    config = pkl.load(PKL_GO_FIXTURES / "unions.pkl")
    assert config.res1 == "two"
    assert config.res2 == "三"


def test_any():
    config = pkl.load(PKL_GO_FIXTURES / "any.pkl")
    assert to_plain(config.res1) == [{"name": "Barney"}]
    assert to_plain(config.res2) == {"name": "Bobby"}
    assert to_plain(config.res3) == {"Wilma": {"name": "Wilma"}}


def test_classes():
    config = pkl.load(PKL_GO_FIXTURES / "classes.pkl")
    assert to_plain(config.myAnimal) == {
        "name": "Uni",
        "barks": False,
        "breed": "Greyhound",
        "canRoach": True,
    }
    assert to_plain(config.animals) == [
        {"name": "Uni", "barks": False, "breed": "Greyhound", "canRoach": True},
        {"name": "Millie", "meows": True},
    ]
    assert to_plain(config.house) == {"area": 2000, "bedrooms": 3, "bathrooms": 2}


def test_dynamic():
    config = pkl.load(FIXTURES / "dynamic.pkl")
    assert to_plain(config.res1) == {"a": "a", "b": {"c": 1, "d": 2}, "e": 3}


def test_intseq():
    config = pkl.load(FIXTURES / "intseq.pkl")
    assert config.res1 == pkl.IntSeq(2, 5, 1)
    assert config.res2 == pkl.IntSeq(5, 2, -2)


def test_regex():
    config = pkl.load(FIXTURES / "regex.pkl")
    assert config.res1 == pkl.Regex("a.b")
    assert config.res2 == pkl.Regex("[0-9]+")


@pytest.mark.xfail(
    strict=True,
    reason=(
        "JAJ-822: pkl-python doesn't decode Bytes (wire code 0x0F) on this baseline "
        "-- the fix already exists upstream as PR #16 / branch "
        "sync/pkl-0.30.0-bytes-decoding, just not merged yet. Once merged, this "
        "should XPASS; strict=True turns that into a failure as a reminder to "
        "remove this marker and assert the real decoded bytes."
    ),
)
def test_bytes():
    config = pkl.load(FIXTURES / "bytes.pkl")
    assert config.res1 == b"\x01\x02\x03"
