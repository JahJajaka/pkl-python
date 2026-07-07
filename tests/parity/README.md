# Parity suite

`pkl-python` has no upstream test suite of its own to check against -- the
official Pkl test suite covers the *evaluator*, not language bindings. The
closest thing to a spec for "did we decode this correctly" is:

1. [The Pkl binary-encoding spec](https://pkl-lang.org/main/current/bindings-specification/message-passing-api.html)
   (the wire format every binding, including pkl-go, decodes).
2. [apple/pkl-go](https://github.com/apple/pkl-go)'s documented/actual behaviour,
   as the most mature reference binding.

This directory is our fact-gate against drift from that reference behaviour: each
test loads a `.pkl` fixture through `pkl.load()` and asserts the decoded Python
value against an expectation grounded in (1) or (2), cited in the test/fixture.

We do **not** shell out to a live pkl-go binary here -- there is no Go toolchain
dependency at test time. "Parity" means matching pkl-go's *documented* behaviour
and checked-in goldens, not a live cross-binding comparison.

## Layout

- `tests/_pkl/*.pkl` -- apple/pkl-go's own vendored `test_fixtures` (note the
  `@go.Package` annotations), already present in this repo. The most direct
  grounding available: these are literally pkl-go's test corpus.
- `tests/parity/fixtures/*.pkl` -- fixtures for value types not covered by the
  above (`IntSeq`, `Regex`, `Bytes`), plus a `Dynamic` example that avoids the
  mixed element/property shape `tests/_pkl/dynamic.pkl` uses (pkl-python's
  parser rejects that shape by design -- see `Parser.parse_typed_dynamic`).
- `test_value_parity.py` -- loads each fixture and asserts the decoded value.
- `test_codegen_parity.py` -- a codegen parity case: runs `pkl-gen-python` on
  the existing `codegen/snippet-tests/input/Simple.pkl` fixture and diffs the
  output against the checked-in golden
  `codegen/snippet-tests/output/com_example_Simple_pkl.py`.

Every test here spawns the real `pkl` evaluator in server mode (directly, or via
`pkl-gen-python`), which hangs in this project's dev sandbox (see JAJ-805/808) --
this suite can only be verified on GitHub Actions (JAJ-821's `ci.yml`).

## Adding a fixture

1. Add a `.pkl` file under `tests/parity/fixtures/` exercising the value type(s)
   you care about. Keep it small and single-purpose.
2. Add a docstring/comment citing where the expected shape comes from: the
   binary-encoding spec, a pkl-go doc/test, or the Pkl standard library docs
   (`https://pkl-lang.org/package-docs/pkl/current/base/...`).
3. Add a test in `test_value_parity.py` that loads the fixture and asserts the
   decoded Python value against that documented expectation. For values that
   decode into pkl-python's dynamically-generated `Dynamic`/`Typed` dataclasses
   (which can't be imported to construct an equal instance), use the `to_plain()`
   helper to compare structurally instead of by class identity.
4. If the fixture surfaces a real decode divergence from the documented/spec
   behaviour, do not fix it in this PR -- capture it (see `test_bytes` for the
   pattern: an `xfail(strict=True)` with a citation) and flag it with
   `needs-pm` for a follow-up bug ticket.
