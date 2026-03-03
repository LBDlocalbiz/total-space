# Storage Site Generator

CLI tool to generate complete, deployment-ready storage facility websites from an Excel data file.

Produces a **static HTML website + blog** matching the BEM CSS architecture with `wss-*` prefix:

- 8 core pages (homepage, about, contact, size guide, FAQs, privacy, terms, 404)
- Dynamic service pages (1-6 services)
- Dynamic city/area pages (1-5 cities)
- Dynamic size guide (1-16 unit types)
- LLM-LD Level 3 Agent-Ready index (`llm-index.json`) for AI discoverability
- Blog with branded header/footer and sample welcome post
- Sitemap, robots.txt, Netlify config, RSS feed

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate a site from Excel data
python generate.py path/to/site-data.xlsx

# Output goes to ./output/{project-name}/ and ./output/{project-name}-blog/
```

## Usage

```bash
# Basic usage (output to ./output/)
python generate.py site-data.xlsx

# Custom output directory
python generate.py site-data.xlsx -o ./my-site/

# Validate Excel only (no generation)
python generate.py site-data.xlsx --validate-only

# Skip blog generation
python generate.py site-data.xlsx --main-only

# Custom blog domain
python generate.py site-data.xlsx --blog-domain https://blog.example.com

# Custom project folder name
python generate.py site-data.xlsx --project-name my-storage-site
```

## Excel File Format

The Excel workbook must contain a **Quick Copy** sheet as the primary data source. Additional sheets (Company Data, Images, City 1-5, Size Guide, Tracking & Schema) provide supplementary data.

### Column format

All data sheets use the same structure:
| Column A | Column B |
|----------|----------|
| `{{BUSINESS_NAME}}` | My Storage Facility |
| `{{DOMAIN}}` | https://example.com |
| `{{PRIMARY_CITY}}` | City Name |

### Required fields

| Category | Fields |
|----------|--------|
| Business | `BUSINESS_NAME`, `DOMAIN`, `PRIMARY_CITY`, `STATE_CODE`, `STATE_FULL`, `ZIP_CODE` |
| Contact | `STREET_ADDRESS`, `PHONE_DISPLAY`, `PHONE_TTC`, `EMAIL_ADDRESS` |
| Branding | `COLOR_PRIMARY` (hex), `COLOR_ACCENT` (hex), `LOGO_TR` (URL) |
| Services | At least 1: `SERVICE_1_NAME`, `SERVICE_1_SLUG` (up to 6) |
| Cities | At least 1: `CITY_1_NAME`, `CITY_1_SLUG` (up to 5) |

### Recommended fields

`BRAND`, `TAGLINE`, `COMPANY_DESCRIPTION`, `HOURS_DISPLAY`, `HERO_HEADLINE`, `HERO_SUBHEADING`, `HERO_IMAGE`, `HOME_META_DESC`, `FACEBOOK_URL`, `GB_MAP_SHARE`, `GB_MAP_EMBED`, `PAY_BILL_URL`, `LATITUDE`, `LONGITUDE`

### Auto-generated defaults

If not provided, the generator creates sensible defaults for:
- Page meta descriptions (about, FAQs, services, size guide)
- Service descriptions, features, and meta descriptions
- City descriptions
- 8 FAQ question/answer pairs

All defaults use the business name, city, and state for location-specific content.

### Excel sheets

| Sheet | Purpose |
|-------|---------|
| Quick Copy | Flat key-value lookup — primary data source |
| Company Data | Business info, location, contact, branding, hero, services |
| Images | Image URLs organized by section |
| City 1-5 | Per-city SEO, local spots, things to do, map embeds |
| Size Guide | 16 unit definitions (size, sqft, description, items, enabled) |
| Tracking & Schema | Analytics pixel IDs, JSON-LD structured data |
| Instructions | Reference guide (not read by generator) |

## Output Structure

```
output/
├── {project-name}/              # Main site → deploy to Netlify
│   ├── index.html               # Homepage with booking widget
│   ├── about.html               # About page
│   ├── contact.html             # Contact with form + map
│   ├── size-guide.html          # Dynamic unit size cards
│   ├── faqs.html                # 8 FAQ accordions + schema
│   ├── privacy.html, terms.html # Legal pages
│   ├── 404.html                 # Custom 404
│   ├── services/
│   │   ├── index.html           # Services listing
│   │   └── *.html               # Individual service pages
│   ├── cities/
│   │   ├── index.html           # Areas listing
│   │   └── *.html               # Individual city pages
│   ├── css/                     # _variables.css + static CSS
│   ├── js/                      # Navigation and UI scripts
│   ├── llm-index.json           # LLM-LD Level 3 AI index
│   ├── sitemap.xml              # Dynamic sitemap
│   ├── robots.txt
│   └── netlify.toml, _redirects # Netlify config
└── {project-name}-blog/         # Blog → deploy to subdomain
    ├── index.html               # Blog home
    ├── posts/
    │   ├── _post-template.html  # Template for writing new posts
    │   └── *-welcome-post.html  # Auto-generated welcome post
    ├── css/, js/
    ├── rss.xml                  # RSS feed
    ├── sitemap.xml, robots.txt
    └── netlify.toml, _redirects
```

## Deployment

### Main site

```bash
cd output/{project-name}
git init && git add -A && git commit -m "Initial site generation"
gh repo create LBDlocalbiz/{project-name} --private --source=. --push
```

Deploy on Netlify: import repo, publish directory `/`, set custom domain.

### Blog

```bash
cd output/{project-name}-blog
git init && git add -A && git commit -m "Initial blog generation"
gh repo create LBDlocalbiz/{project-name}-blog --private --source=. --push
```

Deploy on Netlify: import repo, publish directory `/`, set custom domain (`blog.{domain}`).

### DNS

```
project.beamsstorage.com        CNAME  {netlify-site}.netlify.app
blog.project.beamsstorage.com   CNAME  {netlify-blog}.netlify.app
```

## Project Structure

```
storage-site-generator/
├── generate.py              # CLI entry point
├── requirements.txt         # openpyxl, click
├── generator/               # Python package
│   ├── cli.py               # Click CLI orchestration
│   ├── excel_reader.py      # Excel parsing + content defaults
│   ├── validators.py        # Data validation
│   ├── color_utils.py       # HSL shade generation
│   ├── placeholder_engine.py  # {{KEY}} replacement engine
│   ├── site_builder.py      # Main site generation
│   ├── blog_builder.py      # Blog generation
│   ├── llm_index_builder.py # LLM-LD JSON builder
│   ├── sitemap_builder.py   # Sitemap XML builder
│   └── constants.py         # Field definitions, limits
├── templates/
│   ├── main/                # HTML templates with {{PLACEHOLDER}} tokens
│   └── blog/                # Blog CSS/JS assets
├── setup.md                 # Detailed setup and deployment guide
├── context.md               # Architecture and technical reference
└── sample/                  # Sample Excel template
```

## Dependencies

- `openpyxl` — Excel file parsing
- `click` — CLI interface
- Python 3.8+ (stdlib `colorsys` for color math)

## Documentation

- [setup.md](setup.md) — Installation, Excel format, generation, deployment steps
- [context.md](context.md) — Architecture, pipeline flow, design decisions, placeholder conventions
