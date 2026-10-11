"""Check artifact links, preserved media, source syntax, and directory hygiene."""
import ast
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from layout import FIGURES, REPO, TOOLS


def main() -> None:
    report = json.loads((TOOLS / "organization-report.json").read_text())
    for item in report["preservedFiles"]:
        path = REPO / item["path"]
        with path.open("rb") as source:
            actual = hashlib.file_digest(source, "sha256").hexdigest()
        assert actual == item["sha256"], f"Preserved file changed: {path}"

    links = 0
    documents = [REPO / "README.md", *FIGURES.rglob("*.md"),
                 *(path for path in FIGURES.rglob("*.html") if not path.is_relative_to(TOOLS))]
    for path in documents:
        text = path.read_text()
        urls = (re.findall(r'\]\(([^\s)]+)\)', text) if path.suffix == ".md"
                else re.findall(r'''(?:href|src)=["']([^"']+)["']''', text))
        for url in urls:
            parts = urlsplit(url)
            if parts.scheme or not parts.path:
                continue
            target = (path.parent / unquote(parts.path)).resolve()
            assert target.exists(), f"Broken link in {path}: {url}"
            links += 1

    sources = list(TOOLS.rglob("*.py"))
    for source in sources:
        ast.parse(source.read_text(), filename=str(source))
    forbidden = {".cache", ".venv", "__pycache__", "frames", ".DS_Store"}
    for path in FIGURES.rglob("*"):
        if path.is_relative_to(TOOLS):
            continue
        assert path.name not in forbidden, f"Runtime file in final results: {path}"
        assert path.suffix not in {".py", ".mjs", ".pyc", ".swift"}, path

    print(f"Passed: {len(report['preservedFiles'])} preserved files, "
          f"{links} local links, {len(sources)} Python sources; "
          "no runtime files or production code among finished results.")


if __name__ == "__main__":
    main()
