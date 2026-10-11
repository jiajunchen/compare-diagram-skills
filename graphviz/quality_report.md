# Diagram validation

Graphviz layout, SVG XML, PDF, and PNG checks.

- **01_architecture: PASS** — 16:9 SVG, PDF, and PNG; labeled color swatches; 15 nodes; no node overlaps.
- **02a_entities: PASS** — 16:9 SVG, PDF, and PNG; labeled color swatches; 8 nodes; no node overlaps.
- **02b_object_calls: PASS** — 16:9 SVG, PDF, and PNG; labeled color swatches; 16 nodes; no node overlaps.
- **03a_organization_pathways: PASS** — 9:16 SVG, PDF, and PNG; labeled color swatches; 15 nodes; no node overlaps.
- **03b_media_pathways: PASS** — 9:16 SVG, PDF, and PNG; labeled color swatches; 15 nodes; no node overlaps.

Manual inspection: all five PNG previews were viewed at their native 1920×1080 or 1080×1920 size. Labels are present without clipping. SVG and PDF versions retain vector text for zooming. Colors are paired with text and shape labels, so meaning does not depend on color alone.

Scope: this checks node boxes and file integrity. It does not prove semantic correctness or guarantee that every edge label is free from crossings; those were reviewed against the Swift sources and previews separately.
