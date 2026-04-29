import os
import subprocess
import sys


def run_cli(args):
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    return subprocess.run(
        [sys.executable, "-m", "schemawatch.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


def test_cli_runs():
    result = run_cli(
        [
            "examples/old.yaml",
            "examples/new.yaml",
        ]
    )

    assert result.returncode == 1
    assert "Breaking changes detected" in result.stdout


def test_cli_markdown():
    result = run_cli(
        [
            "examples/old.yaml",
            "examples/new.yaml",
            "--format",
            "markdown",
        ]
    )

    assert result.returncode == 1
    assert "SchemaWatch Report" in result.stdout


def test_cli_no_changes(tmp_path):
    schema = tmp_path / "schema.yaml"

    schema.write_text(
        """
openapi: 3.0.0
paths: {}
components:
  schemas: {}
""",
        encoding="utf-8",
    )

    result = run_cli(
        [
            str(schema),
            str(schema),
        ]
    )

    assert result.returncode == 0
    assert "No breaking changes" in result.stdout