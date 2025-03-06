from pytest_console_scripts import ScriptRunner


def test_project_command(script_runner: ScriptRunner) -> None:
    result = script_runner.run(["data_load_tool", "project", "-h"])
    assert result.returncode == 0

    assert "Usage: data_load_tool project" in result.stdout
