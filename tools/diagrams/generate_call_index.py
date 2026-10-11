"""Generate an exhaustive declaration index for production Swift functions.

This complements the readable cross-component call graph. It is an index of
declarations, not a claim that every private helper is a separate workflow.
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


from pathlib import Path
import re

ROOT = REPO
SOURCE = ROOT / "FencingVideoAnalysis"
OUTPUT = FIGURES / "CALL_INDEX.md"
PATTERN = re.compile(
    r"^\s*(?:(?:private|fileprivate|public|internal|static|class|mutating|"
    r"nonmutating|override|nonisolated|final)\s+)*func\s+([A-Za-z_][A-Za-z_0-9]*)\s*\("
)

groups = {}
total = 0
for path in sorted(SOURCE.rglob("*.swift")):
    matches = []
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        match = PATTERN.match(line)
        if match:
            matches.append((line_number, match.group(1)))
    if matches:
        groups[path.relative_to(ROOT)] = matches
        total += len(matches)

lines = [
    "# Production function declaration index",
    "",
    f"{total} declarations in {len(groups)} Swift files. Generated from the current source tree.",
    "The [object call graph](graphviz/02b_object_calls.svg) shows the cross-component calls; "
    "this index includes internal helpers, view actions, protocol requirements, and fakes.",
    "",
]
for path, matches in groups.items():
    lines.extend([f"## `{path}`", ""])
    for line_number, name in matches:
        lines.append(f"- [`{name}`](../{path.as_posix()}#L{line_number})")
    lines.append("")
OUTPUT.write_text("\n".join(lines))
