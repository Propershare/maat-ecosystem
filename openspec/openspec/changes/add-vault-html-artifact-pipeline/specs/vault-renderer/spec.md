# Spec: vault-renderer

## ADDED Requirements

### Requirement: Single Locked Template
The renderer SHALL use exactly one Jinja2 template (`maatlangchain/maat_vault/templates/vault_entry.html`). The LLM SHALL NOT be permitted to write or modify HTML; the renderer is the only path from `VaultEntry` to HTML.

#### Scenario: Renderer uses the documented template
- **WHEN** `render_entry(entry)` is called
- **THEN** the implementation loads `maatlangchain/maat_vault/templates/vault_entry.html` via Jinja2's `FileSystemLoader`
- **AND** the template name in code is a single literal string (`"vault_entry.html"`), not configurable at runtime
- **AND** the template file is committed to the repo at the documented path

#### Scenario: Template produces valid HTML5
- **WHEN** the rendered output is validated
- **THEN** it begins with `<!doctype html>` (case-insensitive)
- **AND** it contains a single `<html lang="en">` root
- **AND** it has exactly one `<head>` and one `<body>`
- **AND** the W3C HTML5 validator reports zero errors for a representative fixture entry

#### Scenario: Renderer rejects malformed entries
- **WHEN** `render_entry(entry)` is called and `entry.validate()` raises `VaultEntryValidationError`
- **THEN** the renderer propagates the exception (does not silently render a broken page)
- **AND** the exception message is preserved in the log
- **AND** the wiki page file is not written

### Requirement: HTML Document Structure
The rendered HTML SHALL have a fixed structure: `<head>` with metadata + JSON-LD, `<body>` with `<article data-vault-id="...">` containing exactly six sections in this order: header, claims, evidence, body, related, footer.

#### Scenario: Head block carries the documented metadata
- **WHEN** the entry is rendered
- **THEN** `<head>` contains:
  - `<meta charset="utf-8">`
  - `<meta name="viewport" content="width=device-width, initial-scale=1">`
  - `<meta name="vault-id" content="<vault_id>">`
  - `<meta name="source-tier" content="<source_tier>">`
  - `<meta name="status" content="<status>">`
  - `<meta name="author" content="<author>">`
  - `<meta name="created-at" content="<created_at ISO 8601>">`
  - `<meta name="updated-at" content="<updated_at ISO 8601>">`
  - `<title><title></title>` with the entry's title, HTML-escaped
  - `<script type="application/ld+json">{...}</script>` containing the JSON-LD block, indented with `json.dumps(..., indent=2)`

#### Scenario: Body block has the documented section order
- **WHEN** the entry is rendered
- **THEN** `<body>` contains exactly one `<article data-vault-id="<vault_id>">` with the following children, in this order:
  1. `<header class="vault-header">` with `<h1>`, author byline, source-tier badge, status badge, model-used chip (if `model_used` is not None), last-updated timestamp
  2. `<section class="claims">` with `<h2>Key Claims</h2>` and an `<ol>` of claim items
  3. `<section class="evidence">` with `<h2>Provenance & Evidence</h2>` and a `<ul>` of evidence items
  4. `<section class="body">` with `<h2>Body</h2>` and the cleaned `body_text` in `<p>` tags
  5. `<section class="related">` with `<h2>Related Entries</h2>` and a `<ul>` of linked `vault_id`s
  6. `<footer class="vault-footer">` with source tier, status, model used, last-reviewed timestamp, claim count, and a "rendered by vault-router" attribution

#### Scenario: No JavaScript in the rendered HTML
- **WHEN** the entry is rendered
- **THEN** the output contains zero `<script>` tags except the one JSON-LD block
- **AND** zero inline event handlers (`onclick`, `onload`, `onerror`, etc.)
- **AND** the page is fully functional with JavaScript disabled in the browser

#### Scenario: No external resource dependencies
- **WHEN** the entry is rendered
- **THEN** the output contains no `<link rel="stylesheet" href="https://...">` references
- **AND** no `<img src="https://...">` references (assets use relative paths only)
- **AND** no `<iframe>` references
- **AND** the page renders correctly when opened from a `file://` URL with no network access

### Requirement: Provenance Visibility
The rendered HTML SHALL visibly show source tier, status, model used, last-reviewed timestamp, and claim count. A beautiful page with no provenance is propaganda wallpaper — this requirement is non-negotiable.

#### Scenario: Source-tier badge is visible above the fold
- **WHEN** the rendered page is opened in a default browser viewport (1280x800)
- **THEN** the source-tier badge is visible without scrolling
- **AND** the badge has `class="source-tier"` and a `data-tier="<source_tier>"` attribute
- **AND** the badge's CSS makes it visually distinct (different background color per tier)

#### Scenario: Status badge is visible in the header
- **WHEN** the rendered page is opened
- **THEN** the status badge is in the `<header class="vault-header">` block
- **AND** the badge has `class="status-badge"` and a `data-status="<status>"` attribute
- **AND** `disputed` entries show a red badge with a `⚠` glyph
- **AND** `canonical` entries show a green badge with a `✓` glyph

#### Scenario: Model used is shown when present
- **WHEN** the entry has `model_used` set (e.g. `"gemma4:e4b"`)
- **THEN** a `<span class="model-used">model: gemma4:e4b</span>` appears in the header
- **AND** the value matches `entry.model_used` exactly

#### Scenario: Last-reviewed timestamp is shown
- **WHEN** the entry has `updated_at` set
- **THEN** a `<time datetime="<updated_at ISO 8601>">` element appears in the header
- **AND** the human-readable text format is `"last reviewed YYYY-MM-DD"` in UTC
- **AND** the `datetime` attribute is the exact ISO 8601 value from `updated_at`

#### Scenario: Claim count is shown
- **WHEN** the entry has N claims
- **THEN** the footer shows `N claims`
- **AND** the number matches `len(entry.claims)` exactly

### Requirement: Claim Rendering with Confidence
Each claim SHALL be rendered as a list item with a stable fragment id, the claim text, and a visible confidence indicator.

#### Scenario: Each claim is a linkable list item
- **WHEN** the entry is rendered
- **THEN** the claims section contains an `<ol>` with one `<li id="claim-NNN" data-confidence="0.XN">` per claim
- **AND** the `id` matches the `claim_id` in the `VaultEntry.claims` array
- **AND** the `data-confidence` value matches the claim's `confidence` field
- **AND** the claim text is HTML-escaped (no raw HTML injection from claim text)

#### Scenario: Confidence is rendered as a visible indicator
- **WHEN** a claim has `confidence=0.92`
- **THEN** the rendered HTML shows a confidence bar or text indicator reading `92%` or `0.92`
- **AND** the indicator's color reflects the value (e.g. green for ≥0.8, yellow for 0.5–0.8, red for <0.5)
- **AND** claims with no evidence (`evidence_claim_ids == []`) get an `<span class="ungrounded">ungrounded</span>` marker

#### Scenario: Claims with vault_claim evidence link to the related entry
- **WHEN** a claim has an evidence ref with `ref_type="vault_claim"` and `ref_id="vault:other_agent:essay:abcd1234#claim-002"`
- **THEN** the rendered HTML shows an `<a href="#claim-002">` link (if the related entry is co-rendered) or `vault://other_agent:essay:abcd1234#claim-002` (if cross-entry)
- **AND** the link's text is the related claim's text or a `→ claim-002` arrow

### Requirement: Evidence Rendering
Each evidence ref SHALL be rendered as a list item showing the ref type, the ref id (as a stable handle, not a deep link unless known safe), and the optional `note` field.

#### Scenario: Evidence item shows ref type and id
- **WHEN** the entry has an `EvidenceRef(ref_type="canon_chunk", ref_id="chunk:abc123", note="supports chronology")`
- **THEN** the rendered HTML shows `<li data-ref-type="canon_chunk">canon_chunk: chunk:abc123 — supports chronology</li>`
- **AND** the `ref_id` is HTML-escaped
- **AND** the `note` is HTML-escaped

#### Scenario: Evidence is not a deep link by default
- **WHEN** an evidence ref's `ref_id` is not a `vault://` URI
- **THEN** the rendered HTML does NOT generate a clickable hyperlink to that ref
- **AND** the ref id is shown as plain text
- **AND** a future enhancement may add deep links, but this spec requires default-off behavior

### Requirement: Wiki Managed-Block Compatibility
When the rendered HTML is written to a wiki page, it SHALL be wrapped in `<!-- vault:html:start -->` / `<!-- vault:html:end -->` managed-block markers so the existing `memory-wiki` extension's `wiki_lint` flow treats the page as wiki-owned content.

#### Scenario: Wiki page wrapper
- **WHEN** `write_entry_to_wiki(entry, vault_root)` is called
- **THEN** the file written to `<vault_root>/entries/<vault_id>.md` has the structure:
  ```
  <!-- vault:html:start -->
  <!doctype html>
  ...rendered HTML...
  <!-- vault:html:end -->
  ```
- **AND** the file extension is `.md` (not `.html`) to match the existing wiki convention
- **AND** the file is valid Markdown (the HTML block is wrapped in fence-less HTML which Markdown parsers render as raw HTML)

#### Scenario: Wiki lint flags entries with low provenance
- **WHEN** the `memory-wiki` extension's `wiki_lint` is run in `bridge` mode with `vaultBridge.enabled=true`
- **THEN** entries with `maat_score.provenance < 0.3` are flagged as `low_provenance`
- **AND** entries with `status="disputed"` are flagged as `disputed`
- **AND** entries with `source_tier="AI_DRAFT"` and no human review timestamp are flagged as `unreviewed_ai_draft`

#### Scenario: Re-render replaces the managed block in place
- **WHEN** the same `VaultEntry` is re-rendered
- **THEN** the existing `<vault_root>/entries/<vault_id>.md` file has its `<!-- vault:html:start -->` to `<!-- vault:html:end -->` block replaced in place
- **AND** any human-authored content outside the managed markers is preserved
- **AND** the file's `mtime` updates but the path is stable

### Requirement: Determinism
The rendered HTML for a given `VaultEntry` SHALL be byte-identical across calls, modulo the `<meta name="updated-at">` value (which is allowed to vary) and any timestamps in the JSON-LD block (also allowed to vary only in the `dateModified` field).

#### Scenario: Same input produces same output
- **WHEN** `render_entry(entry)` is called twice in succession with the same `VaultEntry` and the same `updated_at` value
- **THEN** the two output strings are byte-identical
- **AND** a unit test fixture verifies this for a representative entry

#### Scenario: Only the timestamp field is allowed to differ
- **WHEN** the same entry is rendered at two different times and `entry.updated_at` has changed
- **THEN** the only difference between the two outputs is the `<meta name="updated-at">` value and the JSON-LD `dateModified` field
- **AND** all other bytes are identical

### Requirement: Security and Escaping
The renderer SHALL HTML-escape all user-controlled fields (`title`, `author`, `body_text`, claim text, evidence notes) and SHALL NOT execute or render any HTML contained in those fields.

#### Scenario: Claim text is HTML-escaped
- **WHEN** a claim's text contains `<script>alert(1)</script>`
- **THEN** the rendered HTML shows `&lt;script&gt;alert(1)&lt;/script&gt;` (escaped)
- **AND** no script tag is present in the output
- **AND** a unit test fixture verifies this for at least one XSS attempt vector

#### Scenario: Title and author are HTML-escaped
- **WHEN** the entry's title contains `<img src=x onerror=alert(1)>` or `&` or `"` or `'`
- **THEN** the rendered HTML escapes all four characters per HTML5 entity rules
- **AND** the `<title>` element does not break out of its quoting

#### Scenario: Body text is paragraphized and escaped
- **WHEN** `entry.body_text` contains multi-paragraph content with newlines
- **THEN** the renderer splits on double-newlines and wraps each paragraph in `<p>...</p>`
- **AND** single newlines within a paragraph become spaces (no `<br>` injection)
- **AND** all HTML metacharacters are escaped
