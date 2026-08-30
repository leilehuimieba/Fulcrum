"""检查根目录入口文档与 docs/ 下 Markdown 的本地链接。"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import unquote, urlsplit

_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+['\"][^'\"]*['\"])?\s*\)")
_REFERENCE_TARGET = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(?:<([^>]+)>|(\S+))")
_IGNORED_SCHEMES = frozenset({"http", "https", "mailto"})


def _ascii_text(value: object) -> str:
    return str(value).encode("ascii", errors="backslashreplace").decode("ascii")


def _markdown_files(root: Path) -> list[Path]:
    files = set(root.glob("*.md"))
    docs = root / "docs"
    if docs.is_dir():
        files.update(docs.rglob("*.md"))
    return sorted(files)


def _targets(path: Path) -> Iterator[tuple[int, str]]:
    fence_char: str | None = None
    fence_length = 0
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        fence = _FENCE.match(line)
        if fence:
            marker = fence.group(1)
            if fence_char is None:
                fence_char = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_length:
                fence_char = None
                fence_length = 0
            continue
        if fence_char is not None:
            continue

        for match in _INLINE_LINK.finditer(line):
            yield line_number, match.group(1) or match.group(2)
        reference = _REFERENCE_TARGET.match(line)
        if reference:
            yield line_number, reference.group(1) or reference.group(2)


def _resolve_local_target(source: Path, target: str) -> Path | None:
    parsed = urlsplit(target)
    if parsed.scheme.lower() in _IGNORED_SCHEMES or parsed.netloc:
        return None
    if not parsed.path:
        return None

    decoded = unquote(parsed.path)
    return (source.parent / decoded).resolve()


def check_links(root: Path) -> tuple[list[Path], list[tuple[Path, int, str]]]:
    root = root.resolve()
    files = _markdown_files(root)
    broken: list[tuple[Path, int, str]] = []
    for source in files:
        for line_number, target in _targets(source):
            try:
                resolved = _resolve_local_target(source, target)
            except ValueError:
                broken.append((source.relative_to(root), line_number, target))
                continue
            if resolved is not None and (
                not resolved.is_relative_to(root) or not resolved.exists()
            ):
                broken.append((source.relative_to(root), line_number, target))
    return files, broken


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="检查 Markdown 本地链接是否存在")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="仓库根目录")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        print(f"Repository root does not exist: {_ascii_text(root)}", file=sys.stderr)
        return 2

    files, broken = check_links(root)
    if broken:
        for source, line_number, target in broken:
            print(
                f"{_ascii_text(source.as_posix())}:{line_number}: broken link: "
                f"{_ascii_text(target)}",
                file=sys.stderr,
            )
        print(f"Markdown local link check failed: {len(broken)} broken", file=sys.stderr)
        return 1

    print(f"Markdown local link check passed: {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
