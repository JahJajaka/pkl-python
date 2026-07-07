from pathlib import Path

from pkl_gen_python import (
    GeneratorSettings,
    get_generator_settings_file,
    load_generator_settings,
)


def test_get_generator_settings_file_returns_explicit_path_unchanged():
    assert get_generator_settings_file("custom-settings.pkl") == "custom-settings.pkl"


def test_get_generator_settings_file_returns_none_when_absent_from_cwd(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    assert get_generator_settings_file(None) is None


def test_get_generator_settings_file_detects_default_file_in_cwd(tmp_path, monkeypatch):
    # Parity with apple/pkl-go v0.13.1 (apple/pkl-go#214), which fixed pkl-go's Go
    # CLI failing to detect a generator-settings.pkl in the working directory.
    # pkl-python resolves this in Python via Path.exists() rather than Pkl's
    # read?(), so it never had the underlying bug, but we lock in the behavior.
    (tmp_path / "generator-settings.pkl").write_text('amends "pkl:GeneratorSettings"\n')
    monkeypatch.chdir(tmp_path)

    assert get_generator_settings_file(None) == Path("generator-settings.pkl")


def test_load_generator_settings_defaults_when_no_file_in_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert load_generator_settings(None) == GeneratorSettings()
