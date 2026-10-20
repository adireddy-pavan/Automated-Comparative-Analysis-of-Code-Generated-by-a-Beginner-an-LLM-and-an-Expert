"""Windows-specific CLI resolution regression check (no Windows host required)."""
from pathlib import Path
from src import utils


def test_windows_venv_cli_suffix():
    for executable in ("radon", "pylint", "bandit"):
        path = utils.analysis_tool_path(executable, on_windows=True)
        assert path.lower().endswith(executable + ".exe")
        assert Path(path).parent == Path(utils.sys.executable).parent


def test_unix_venv_cli_has_no_exe_suffix():
    assert utils.analysis_tool_path("radon", on_windows=False).endswith("radon")
