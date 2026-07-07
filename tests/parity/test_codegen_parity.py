"""
Codegen parity: pkl-gen-python's output for a schema fixture must keep matching a
checked-in golden Python file. Reuses the existing codegen/snippet-tests/ input/output
precedent and the local-generator harness from tests/test_class_ordering.py, rather
than duplicating a fixture -- any drift in generated code (formatting, ordering,
naming) fails this test until the golden is deliberately updated.
"""

from pathlib import Path

from tests.test_class_ordering import generate_with_local_generator

SNIPPET_INPUT = (
    Path(__file__).parent.parent.parent / "codegen" / "snippet-tests" / "input"
)
SNIPPET_OUTPUT = (
    Path(__file__).parent.parent.parent / "codegen" / "snippet-tests" / "output"
)


def test_simple_pkl_codegen_matches_golden(tmp_path):
    pkl_file = SNIPPET_INPUT / "Simple.pkl"
    golden_file = SNIPPET_OUTPUT / "com_example_Simple_pkl.py"

    result = generate_with_local_generator(str(pkl_file), str(tmp_path))
    assert result.returncode == 0, f"Code generation failed: {result.stderr}"

    generated_file = tmp_path / "com_example_Simple_pkl.py"
    assert generated_file.exists(), f"Generated file not found: {generated_file}"
    assert generated_file.read_text() == golden_file.read_text()
