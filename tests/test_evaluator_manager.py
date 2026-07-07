import pytest

from pkl import EvaluatorManager, EvaluatorOptions, ModuleSource, PreconfiguredOptions


# TODO(JAJ-819 follow-up): manager.new_evaluator(EvaluatorOptions()) hangs
# indefinitely on a real pkl server (confirmed on a clean GitHub Actions
# runner, not just the dev sandbox) -- times out reading the CreateEvaluator
# response in src/pkl/server.py's PKLServer.receive(). See JAJ-821.
@pytest.mark.skip(reason="JAJ-819 follow-up: real evaluator hang, see server.py PKLServer.receive")
def test_manager():
    with EvaluatorManager(debug=True) as manager:
        manager.new_evaluator(EvaluatorOptions())


def test_multiple():
    with EvaluatorManager(debug=True) as manager:
        opts = PreconfiguredOptions()
        evaluator = manager.new_evaluator(opts)
        source = ModuleSource.from_path("./tests/pkls/with_log.pkl")
        evaluator.evaluate_module(source)
