# Context — Storage Site Generator

## What This Is

A Python CLI tool that generates complete, deployment-ready static HTML websites for self-storage facilities. Given an Excel workbook with business data, it produces:

1. A **main site** (8 core pages + dynamic service/city/size-guide pages)
2. A **blog site** (index + welcome post + post template)
3. An **LLM-LD index** (`llm-index.json`) for AI discoverability

The output is two static folders ready to push to GitHub and deploy on Netlify.

## Architecture Overview

```
generate.py                          CLI entry point
    └── generator/
        ├── cli.py                   Click CLI — orchestrates the full pipeline
        ├── excel_reader.py          Excel → flat dict (reads all 11 sheets)
        ├── validators.py            Validates required fields, hex colors
        ├── color_utils.py           HSL shade generation from primary/accent hex
        ├── placeholder_engine.py    {{KEY}} → value replacement engine
        ├── site_builder.py          Main site generation (dynamic pages, footer, schema)
        ├── blog_builder.py          Blog generation (programmatic HTML, not template-based)
        ├── llm_index_builder.py     LLM-LD Level 3 Agent-Ready JSON builder
        ├── sitemap_builder.py       Dynamic sitemap.xml generation
        └── constants.py             Field definitions, max counts, icons
```

## Pipeline Flow

```
Excel file
    │
    ▼
excel_reader.py ── reads all sheets ──► flat dict (492+ key-value pairs)
    │                                        │
    ▼                                        ▼
validators.py ── checks required fields    _fill_content_defaults() ── generates
    │            validates hex colors       missing service/city/FAQ/meta content
    ▼
color_utils.py ── generates CSS variables from COLOR_PRIMARY and COLOR_ACCENT
    │              (50/100/200/300/400/600/700/800/900/950 shades via HSL)
    ▼
site_builder.py ── processes templates through placeholder_engine
    │   ├── Core pages: index, about, contact, size-guide, faqs, privacy, terms, 404
    │   ├── Dynamic service pages: 1-6 from _service-template.html
    │   ├── Dynamic city pages: 1-5 from _city-template.html
    │   ├── Dynamic size guide: 1-16 unit cards based on UNIT_N_ENABLED
    │   ├── Dynamic footer: rebuilds service links for actual count
    │   ├── Dynamic homepage: rebuilds services/cities/schema sections
    │   └── Static assets: CSS, JS, netlify.toml, _redirects, robots.txt, sitemap.xml
    ▼
llm_index_builder.py ── builds llm-index.json (Level 3 Agent-Ready)
    ▼
blog_builder.py ── generates blog programmatically
    ├── index.html with branded header/footer
    ├── Welcome post
    ├── _post-template.html
    ├── rss.xml, sitemap.xml, robots.txt
    └── CSS _variables.css (same color shades as main site)
```

## Key Design Decisions

### Template approach (main site)
The main site uses **file-based templates** stored in `templates/main/`. These are real HTML files with `{{PLACEHOLDER}}` tokens. The `placeholder_engine.py` performs string replacement — no Jinja2 or templating library needed.

### Blog approach (programmatic)
The blog is generated **programmatically** via `blog_builder.py` using Python f-strings. This avoids the complexity of templatizing the Winston blog's hardcoded values. The blog header/footer uses absolute URLs to the main domain.

### Dynamic page generation
Templates use a convention where `SERVICE_X` and `CITY_X` are placeholder prefixes. The engine:
1. Copies the template for each service/city
2. Replaces `SERVICE_X` → `SERVICE_1`, `SERVICE_2`, etc.
3. Rebuilds "Other Services"/"Other Areas" sections to exclude the current item
4. Adjusts CSS grid classes based on actual count

### Color system
A single hex color (`COLOR_PRIMARY`) generates a full shade palette (50-950) using HSL lightness manipulation via stdlib `colorsys`. This produces the `_variables.css` file that the BEM CSS architecture depends on.

### Content defaults
The `_fill_content_defaults()` function in `excel_reader.py` auto-generates content for fields not provided in the Excel:
- Page meta descriptions derived from business name + location
- Service descriptions and features derived from service names
- City descriptions derived from city names + facility address
- 8 FAQ Q&A pairs with generic self-storage content
- All defaults are location-aware (use business name, city, state, phone)

### LLM-LD specification
The `llm-index.json` follows the LLM-LD v1 specification at Level 3 (Agent-Ready). It includes:
- Site metadata, conformance declaration
- Primary entity (SelfStorage schema)
- Business summary with key facts and differentiators
- Service catalog with actions
- Full page directory with types and schemas
- Contact channels with hours
- Decision guidance for AI agents
- Capabilities, boundaries, and authority declarations

## Excel Data Flow

The Excel workbook has 11 sheets. The reader processes them in this order:

1. **Quick Copy** (primary) — flat key-value of all placeholders, read first
2. **Company Data** — business info, location, branding, services, hero (supplements Quick Copy)
3. **Images** — all image URLs by section
4. **Tracking & Schema** — analytics IDs, JSON-LD schemas
5. **Size Guide** — 16 unit definitions with enabled/disabled flag
6. **City 1-5** — per-city SEO, local spots, things to do

Quick Copy values take priority. Supplementary sheets only fill in keys not already present.

## Placeholder Conventions

| Pattern | Example | Used In |
|---------|---------|---------|
| `{{KEY}}` | `{{BUSINESS_NAME}}` | All pages |
| `{{SERVICE_X_*}}` | `{{SERVICE_X_NAME}}` | `_service-template.html` — X gets replaced with 1, 2, 3... |
| `{{CITY_X_*}}` | `{{CITY_X_NAME}}` | `_city-template.html` — X gets replaced with 1, 2, 3... |
| `{{UNIT_N_*}}` | `{{UNIT_1_SIZE}}` | `size-guide.html` — built dynamically for enabled units |
| `{{FAQ_N_*}}` | `{{FAQ_1_QUESTION}}` | `faqs.html` — 8 Q&A pairs |
| `{{IMAGE_*}}` | `{{IMAGE_S1L}}` | Various pages — S=service, L=landscape, P=portrait |

## CSS Architecture

BEM naming with `wss-*` prefix (Winston Self Storage). All custom properties defined in `css/_variables.css`:

```css
--wss-primary-50 through --wss-primary-950   /* Generated from COLOR_PRIMARY */
--wss-accent-600                              /* Generated from COLOR_ACCENT */
--wss-text-*, --wss-shadow-*, --wss-rounded-* /* Static design tokens */
```

## Output Structure

```
output/
├── {project-name}/                  # Main site → Netlify
│   ├── index.html                   # Homepage with booking widget
│   ├── about.html                   # About page
│   ├── contact.html                 # Contact with form + map
│   ├── size-guide.html              # Dynamic unit cards (1-16)
│   ├── faqs.html                    # 8 FAQ accordions + FAQPage schema
│   ├── privacy.html, terms.html     # Legal pages
│   ├── 404.html                     # Custom 404
│   ├── services/
│   │   ├── index.html               # Service listing with cards
│   │   └── {slug}.html              # 1-6 individual service pages
│   ├── cities/
│   │   ├── index.html               # Area listing with cards
│   │   └── {slug}.html              # 1-5 individual city pages
│   ├── css/                         # _variables.css + static CSS
│   ├── js/main.js                   # Navigation, accordion, scroll
│   ├── llm-index.json               # LLM-LD Level 3 AI index
│   ├── sitemap.xml                  # Dynamic sitemap
│   ├── robots.txt                   # With sitemap reference
│   ├── netlify.toml                 # Headers, caching, CORS
│   └── _redirects                   # Netlify redirects
└── {project-name}-blog/             # Blog → Netlify subdomain
    ├── index.html                   # Blog home with post listing
    ├── posts/
    │   ├── _post-template.html      # Template for new posts
    │   └── {date}-welcome-post.html # Auto-generated welcome post
    ├── css/                         # Same color variables
    ├── js/main.js                   # Blog navigation
    ├── rss.xml                      # RSS feed
    ├── sitemap.xml, robots.txt
    └── netlify.toml, _redirects
```

## Dependencies

- `openpyxl` — Excel (.xlsx) file parsing
- `click` — CLI argument/option handling
- Python stdlib `colorsys` — HSL color math
- Python stdlib `json`, `re`, `shutil`, `pathlib`, `datetime`

No templating engine, no build tools, no JavaScript bundler.

## Limitations

- Maximum 6 services, 5 cities, 16 unit sizes (defined in `constants.py`)
- Blog is generated programmatically — no template customization beyond colors/branding
- No image optimization or resizing — images must be pre-uploaded to S3/CDN
- No JavaScript framework — vanilla JS only
- GTM replacement looks for the hardcoded ID `GTM-PCG3NH9N` in templates
- Generated default content is generic — should be replaced with unique copy for SEO
