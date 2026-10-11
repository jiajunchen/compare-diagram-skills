"""Reapply this workspace's fullscreen fix after reinstalling the ignored skill."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


import argparse
from pathlib import Path


DEFAULT_SKILL = REPO / ".agents/skills/architecture-diagram"


def replace_once(source, old, new):
    if new in source:
        return source
    if source.count(old) != 1:
        raise ValueError(f"Expected one template anchor: {old[:60]}")
    return source.replace(old, new, 1)


def patch_template(template):
    page = template.read_text()
    if "body.diagram-fullscreen main{" not in page:
        page = replace_once(
            page,
            "  /* fullscreen canvas */",
            "  /* fullscreen canvas */\n"
            "  /* Raise main above the page header while its canvas is fixed. */\n"
            "  body.diagram-fullscreen{ overflow:hidden; }\n"
            "  body.diagram-fullscreen main{ z-index:10000; }")
    page = replace_once(
        page,
        "  .canvas.is-fullscreen .stage{ height: calc(100vh - 80px); }",
        "  .canvas.is-fullscreen .stage{ height:max(460px, calc(100vh - 160px)); }")
    page = replace_once(
        page,
        '  canvas.classList.toggle("is-fullscreen");',
        '  canvas.classList.toggle("is-fullscreen");\n'
        '  document.body.classList.toggle("diagram-fullscreen", canvas.classList.contains("is-fullscreen"));')
    assert "body.diagram-fullscreen main{ z-index:10000; }" in page
    assert 'document.body.classList.toggle("diagram-fullscreen"' in page
    template.write_text(page)


def patch_guide(skill_guide):
    guide = skill_guide.read_text()
    guide = replace_once(guide, "version: 1.3.0\n", "metadata:\n  version: 1.3.0\n")
    reminder = ("- [ ] In fullscreen, confirm the page header stays behind the canvas, "
                "the canvas title clears the nodes, and Escape restores the normal page. "
                "Check a narrow viewport too.\n")
    if reminder not in guide:
        anchor = "- [ ] Did you generate the companion `architecture.md`?"
        if guide.count(anchor) != 1:
            raise ValueError("Expected one skill validation checklist anchor")
        guide = guide.replace(anchor, reminder + anchor, 1)
    skill_guide.write_text(guide)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, default=DEFAULT_SKILL)
    skill = parser.parse_args().skill_dir.resolve()
    template = skill / "assets/template.html"
    guide = skill / "SKILL.md"
    if not template.is_file() or not guide.is_file():
        raise SystemExit(f"Install architecture-diagram in {skill} first")
    patch_template(template)
    patch_guide(guide)
    print(f"Architecture diagram skill fullscreen fix is present in {skill}")
