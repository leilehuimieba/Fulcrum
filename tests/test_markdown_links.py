"""Markdown 本地链接门禁的命令行回归。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_CHECKER = Path(__file__).resolve().parents[1] / "scripts" / "check_markdown_links.py"


def _run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_CHECKER), "--root", str(root)],
        capture_output=True,
        check=False,
        text=True,
    )


def test_checker_accepts_existing_local_targets_and_ignores_non_files(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    assets = tmp_path / "assets"
    docs.mkdir()
    assets.mkdir()
    (tmp_path / "README.md").write_text(
        """# Home

[guide](docs/guide.md#details)
[assets](assets/)
[external](https://example.invalid/docs)
[mail](mailto:security@example.invalid)
[same page](#home)
[reference][guide-ref]

[guide-ref]: docs/guide.md
""",
        encoding="utf-8",
    )
    (docs / "guide.md").write_text(
        """# Guide

[home](../README.md)

```markdown
[example only](missing-example.md)
```
""",
        encoding="utf-8",
    )

    completed = _run_checker(tmp_path)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Markdown local link check passed" in completed.stdout
    assert completed.stdout.isascii()


def test_checker_reports_broken_link_with_source_line(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("[missing](docs/missing.md)\n", encoding="utf-8")

    completed = _run_checker(tmp_path)

    output = completed.stdout + completed.stderr
    assert completed.returncode == 1
    assert "README.md:1" in output
    assert "docs/missing.md" in output


def test_checker_escapes_unicode_in_failure_output(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "文档.md").write_text("[missing](不存在.md)\n", encoding="utf-8")

    completed = _run_checker(tmp_path)

    assert completed.returncode == 1
    assert (completed.stdout + completed.stderr).isascii()


def test_checker_reports_malformed_url_without_traceback(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("[invalid](http://[)\n", encoding="utf-8")

    completed = _run_checker(tmp_path)

    assert completed.returncode == 1
    assert "broken link: http://[" in completed.stderr
    assert "Traceback" not in completed.stderr
