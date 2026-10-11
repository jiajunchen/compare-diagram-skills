# Architecture atlas style guide

Artifact-scoped interpretation of the user's Maria Vasilyeva portfolio reference. No installed skill, project profile, or global design settings were changed.

| Role | Value | Evidence |
|---|---|---|
| paper | #f9f9f9 | Portfolio body / --white |
| ink | #131313 | Portfolio body text / --black |
| muted / soft | #585858 | Supporting gray in portfolio CSS |
| paper-2 | #eeeeec | Derived neutral for stored state |
| rule-solid | #b8b8b5 | Derived visible border |
| rule | rgba(19,19,19,.12) | Derived ink hairline |
| accent | #131313 | Intentional monochrome interpretation of user reference |
| accent-tint | #eeeeec | Derived neutral |
| link | #585858 | Monochrome external relationship |

Focal nodes use inverse paper text on ink. This intentionally replaces the skill's saturated-accent default with the user's monochrome reference. No shadows. Six nodes and at most six connectors per figure. 1280 × 720 doc-wide SVG canvases, local horizontal scrolling, static rendering.

## Font fidelity receipt

Sampled https://www.mariavasilyeva.com/ on October 9, 2026, reached through https://www.awwwards.com/sites/maria-vasilyeva-portfolio.

- Heading: `feat`, weight 400, custom-hosted `/fonts/feat-4.woff2` → fallback Instrument Serif 400.
- Body/navigation: `synt`, weight 400, custom-hosted `/fonts/synt-4.woff2` → fallback Geist 400/500/600 for readable diagram names.
- Supporting copy: `suo`, weight 400, custom-hosted `/fonts/suo-4.woff2`.
- Technical labels: fallback Geist Mono 400/500; the reference has no inspected code block defining a dedicated technical-label family.
- Public substitutes: Google Fonts CSS2 endpoint. All three substitutes were confirmed loaded in Chrome.
- Typography is an interpretation, not an exact font match. No custom font files copied.

The portfolio's animated opening was captured during loading. Computed styles and its inline/CSS tokens are the basis for the palette and font receipt; no claim is made to replicate the entire moving page.
