# Tehuti Search - Maat-Aligned Web Search

**Privacy-focused metasearch with source quality scoring and RBG Library integration.**

## Features

- ✅ SearXNG-powered web search
- ✅ Maat-aligned source quality scoring (A/B/C bands)
- ✅ Three-ring classification (canonical/provisional/draft)
- ✅ UKMT/RBG source detection
- ✅ PDF discovery and metadata
- ✅ RBG Library cross-referencing

## Setup

### 1. Start SearXNG

```bash
cd /home/suspect/.n8n/tehuti-search
docker-compose up -d
```

### 2. Start Tehuti Search MCP

```bash
sudo systemctl daemon-reload
sudo systemctl enable mcpo-tehuti-search
sudo systemctl start mcpo-tehuti-search
```

### 3. Verify

```bash
# Check SearXNG
curl http://127.0.0.1:8080

# Check MCP
curl http://127.0.0.1:8022/openapi.json
```

## MCP Tools

- `search_web` - Web search with quality scoring
- `search_pdfs` - PDF-specific search
- `get_source_quality` - Analyze URL quality
- `cross_reference_rbg` - Match with RBG Library

## Maat Principles

- **Truth**: Quality scoring based on source rigor
- **Balance**: Multiple perspectives, no single source bias
- **Order**: Structured results with classification
- **Reciprocity**: Full source attribution

