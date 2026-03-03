# Setup Guide — Storage Site Generator

## Prerequisites

- **Python 3.8+** installed and available as `python` or `python3`
- **pip** package manager
- **Git** and **GitHub CLI** (`gh`) for deployment
- A completed **Excel data file** (see Excel Format below)

## Installation

```bash
# Clone the repo
git clone https://github.com/LBDlocalbiz/storage-site-generator.git
cd storage-site-generator

# Install Python dependencies
pip install -r requirements.txt
```

Only two dependencies: `openpyxl` (Excel parsing) and `click` (CLI).

## Preparing the Excel Data File

The Excel workbook drives all site content. It must contain these sheets:

| Sheet | Purpose |
|-------|---------|
| **Quick Copy** | Flat key-value lookup of all placeholders (primary data source) |
| **Company Data** | Business info, location, contact, branding, hero section, services, keywords |
| **Images** | All image URLs organized by section (backgrounds, homepage, services) |
| **City 1** through **City 5** | Per-city SEO, local spots, things to do, map embeds |
| **Size Guide** | 16 storage unit definitions (size, sqft, description, items, enabled flag) |
| **Tracking & Schema** | Analytics pixel IDs and JSON-LD structured data |
| **Instructions** | Reference only — not read by generator |

### Column format

Every data sheet uses the same structure:
- **Column A**: Placeholder key wrapped in `{{...}}` (e.g., `{{BUSINESS_NAME}}`)
- **Column B**: Value for that placeholder
- **Column C** (optional): Description/notes

### Required fields (minimum to generate)

```
BUSINESS_NAME, DOMAIN, PRIMARY_CITY, STATE_CODE, STATE_FULL, ZIP_CODE
STREET_ADDRESS, PHONE_DISPLAY, PHONE_TTC, EMAIL_ADDRESS
COLOR_PRIMARY (hex, e.g. #1E3A5F), COLOR_ACCENT (hex)
LOGO_TR (transparent logo URL)
At least 1 service: SERVICE_1_NAME, SERVICE_1_SLUG
At least 1 city: CITY_1_NAME, CITY_1_SLUG
```

### Auto-generated defaults

If these fields are missing from the Excel, the generator creates sensible defaults:

- **Page meta descriptions**: `ABOUT_META_DESC`, `FAQS_META_DESC`, `SERVICES_META_DESC`, `SIZEGUIDE_META_DESC`
- **Service details**: `SERVICE_N_SHORT_DESC`, `SERVICE_N_FULL_DESC`, `SERVICE_N_META_DESC`, `SERVICE_N_FEATURE_1-4`
- **City descriptions**: `CITY_N_FULL_DESC`
- **FAQ content**: 8 generic self-storage FAQ Q&A pairs

These defaults use the business name, city, and state from the Excel to create location-specific content. Override them by adding the corresponding keys to your Excel file.

## Generating a Site

### Basic generation

```bash
python generate.py path/to/site-data.xlsx
```

Output goes to `./output/{business-name}/` and `./output/{business-name}-blog/`.

### CLI options

```bash
python generate.py site-data.xlsx -o ./my-output/          # Custom output directory
python generate.py site-data.xlsx --validate-only           # Validate Excel only
python generate.py site-data.xlsx --main-only               # Skip blog generation
python generate.py site-data.xlsx --blog-domain https://blog.example.com
python generate.py site-data.xlsx --project-name my-site    # Custom folder name
```

### Validation

Run `--validate-only` first to check your Excel file:

```bash
python generate.py site-data.xlsx --validate-only
```

This reports errors (missing required fields) and warnings (missing optional fields) without generating any files.

## Deploying to Netlify

After generation, you have two folders to deploy separately:

### 1. Main site

```bash
cd output/{project-name}
git init
git add -A
git commit -m "Initial site generation"
gh repo create LBDlocalbiz/{project-name} --private --source=. --push
```

Then in Netlify:
1. Import the GitHub repo
2. Build command: leave blank (static site)
3. Publish directory: `/`
4. Set custom domain (e.g., `project.beamsstorage.com`)

### 2. Blog

```bash
cd output/{project-name}-blog
git init
git add -A
git commit -m "Initial blog generation"
gh repo create LBDlocalbiz/{project-name}-blog --private --source=. --push
```

Then in Netlify:
1. Import the GitHub repo
2. Build command: leave blank
3. Publish directory: `/`
4. Set custom domain (e.g., `blog.project.beamsstorage.com`)

### DNS configuration

For each custom domain, add a CNAME record:
```
project.beamsstorage.com        CNAME  {netlify-site}.netlify.app
blog.project.beamsstorage.com   CNAME  {netlify-blog-site}.netlify.app
```

## Post-Generation Checklist

After deploying, review and customize:

1. **Hero section** — Update `HERO_IMAGE`, `HERO_HEADLINE`, `HERO_SUBHEADING` in Excel if using defaults
2. **Service descriptions** — Replace auto-generated descriptions with unique content for SEO
3. **City descriptions** — Replace auto-generated descriptions with location-specific content
4. **FAQ answers** — Customize the 8 FAQ answers with facility-specific details
5. **Images** — Ensure all S3 image URLs are uploaded and accessible
6. **Tracking** — Add GTM, GA4, or other pixel IDs to the Tracking & Schema sheet
7. **Blog posts** — Write and publish blog posts using `posts/_post-template.html`
8. **LLM-LD index** — Review `llm-index.json` for accuracy

## Updating an Existing Site

To regenerate after updating the Excel:

```bash
# Re-run the generator (overwrites output)
python generate.py site-data.xlsx -o ./output/

# In the output directory, commit and push changes
cd output/{project-name}
git add -A
git commit -m "Update site content from Excel"
git push
```

Netlify auto-deploys on push.
