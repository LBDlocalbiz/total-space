# Self Storage Single Facility Website Template

## Overview

This template creates a static HTML website for a single self-storage facility with StorEdge integration. It requires NO build step and deploys directly to Netlify.

**Important:** All data comes from the provided Excel file. The Excel file contains ALL placeholder values that need to be replaced in the template files.

---

## Quick Start for Claude Instances

### Step 1: Read the Excel File

The user will provide an Excel file with the following sheets:

| Sheet | Purpose |
|-------|---------|
| **Company Data** | Business name, address, phone, email, hours, branding |
| **Images** | All image URLs (backgrounds, homepage, services, OG images) |
| **City 1-5** | City pages data (name, slug, image, map embed, SEO, local spots) |
| **Size Guide** | Unit sizes, descriptions, images, what fits |
| **Tracking & Schema** | GTM, GA4, pixels, schema markup |
| **Quick Copy** | Consolidated list of all placeholders for easy reference |

### Step 2: Replace Placeholders

All placeholders use the `{{PLACEHOLDER_NAME}}` syntax. Replace them with values from the Excel file.

**Critical placeholders to replace first:**

```
{{BUSINESS_NAME}}        - Full business name
{{DOMAIN}}               - Website URL (e.g., https://example.com/)
GTM-PCG3NH9N     - Google Tag Manager ID
{{PHONE_DISPLAY}}        - Display phone (e.g., (555) 123-4567)
{{PHONE_TTC}}            - Click-to-call phone (e.g., +15551234567)
{{LOGO_TR}}              - Transparent logo URL
{{COLOR_PRIMARY}}        - Primary brand color hex (e.g., #1E3A5F)
```

### Step 3: Generate Color Shades

From the primary color, generate shade variants for the CSS variables file:

```css
--wss-primary: {{COLOR_PRIMARY}};        /* Base color */
--wss-primary-50: /* 95% lighter */
--wss-primary-100: /* 90% lighter */
--wss-primary-200: /* 80% lighter */
--wss-primary-300: /* 70% lighter */
--wss-primary-400: /* 60% lighter */
--wss-primary-500: /* Same as primary */
--wss-primary-600: /* 10% darker */
--wss-primary-700: /* 20% darker */
--wss-primary-800: /* 30% darker */
--wss-primary-900: /* 40% darker */
--wss-primary-950: /* 50% darker */
```

Use a tool like https://www.tailwindshades.com/ or calculate programmatically.

---

## File Structure

```
{{PROJECT_FOLDER_NAME}}/
├── index.html                  # Homepage
├── about.html                  # About Us
├── contact.html                # Contact page
├── size-guide.html             # Storage unit size guide
├── faqs.html                   # FAQs with accordion
├── privacy.html                # Privacy Policy
├── terms.html                  # Terms & Conditions
├── 404.html                    # Custom 404 page
├── services/
│   ├── index.html              # Services overview
│   └── [service-slug].html     # Individual service pages (4-6)
├── cities/
│   ├── index.html              # Service areas overview
│   └── [city-slug].html        # Individual city pages (up to 5)
├── css/
│   ├── styles.css              # Main entry (imports partials)
│   ├── _variables.css          # CSS custom properties (EDIT THIS)
│   ├── _base.css               # Reset, typography
│   ├── _components.css         # BEM components
│   └── _layouts.css            # Container, grid, sections
├── js/
│   └── main.js                 # Mobile menu toggle
├── terms and policy/           # Source legal documents (if provided)
├── data/
│   └── site-data.xlsx          # Excel file with all data
├── netlify.toml                # Netlify config
├── _redirects                  # Netlify redirects
├── robots.txt                  # Search engine directives
└── sitemap.xml                 # XML sitemap
```

---

## Pages to Create

### Required Pages (always create)

1. **index.html** - Homepage with hero, unit booking embed, features, services, areas, map
2. **about.html** - About page with Corporation schema
3. **contact.html** - Contact form + info + map
4. **size-guide.html** - Unit sizes with images and descriptions
5. **faqs.html** - FAQs with FAQPage schema
6. **privacy.html** - Privacy Policy (noindex)
7. **terms.html** - Terms & Conditions (noindex)
8. **404.html** - Custom 404 page
9. **services/index.html** - Services overview page

### Service Pages (4-6 based on Excel)

Create a page for each service listed in Company Data:
- `/services/{{SERVICE_1_SLUG}}.html`
- `/services/{{SERVICE_2_SLUG}}.html`
- `/services/{{SERVICE_3_SLUG}}.html`
- `/services/{{SERVICE_4_SLUG}}.html`

### City Pages (up to 5 based on Excel)

Create a page for each city with data in City 1-5 sheets:
- `/cities/{{CITY_1_SLUG}}.html`
- `/cities/{{CITY_2_SLUG}}.html`
- etc.

---

## Complete Placeholder Reference

### Business Information
```
{{BUSINESS_NAME}}           - Full business name
{{BRAND}}                   - Brand name (may be same as business)
{{PROJECT_FOLDER_NAME}}     - Folder name (lowercase, hyphens)
{{TAGLINE}}                 - Business tagline
{{DOMAIN}}                  - Full website URL with trailing slash
{{CURRENT_YEAR}}            - Year for copyright
{{COMPANY_DESCRIPTION}}     - Full company description
```

### Location
```
{{STREET_ADDRESS}}          - Street address
{{PRIMARY_CITY}}            - Main city
{{STATE_CODE}}              - State abbreviation (e.g., NC)
{{STATE_FULL}}              - Full state name (e.g., North Carolina)
{{ZIP_CODE}}                - ZIP/postal code
{{COUNTY_1}}                - County name
{{LATITUDE}}                - Geo latitude
{{LONGITUDE}}               - Geo longitude
```

### Contact
```
{{PHONE_DISPLAY}}           - Formatted phone (e.g., (336) 348-7867)
{{PHONE_TTC}}               - Click-to-call (e.g., +13363487867)
{{EMAIL_ADDRESS}}           - Email address
{{HOURS_DISPLAY}}           - Hours display text
{{CONTACT_NAME}}            - Contact person name
{{CONTACT_MOBILE}}          - Contact mobile number
```

### Google Business / Maps
```
{{GB_MAP_EMBED}}            - Google Maps iframe embed code
{{GB_MAP_SHARE}}            - Google Maps share URL
{{GB_REVIEW_URL}}           - Google review URL
```

### StorEdge / Booking
```
{{RENTAL_PORTAL_EMBED}}     - StorEdge/Storrd iframe embed
{{PAY_BILL_URL}}            - Pay bill portal URL
{{REVIEWS_WIDGET}}          - Reviews widget code (if any)
```

### Branding
```
{{LOGO_URL}}                - Main logo URL
{{LOGO_TR}}                 - Transparent logo URL
{{LOGO_WH}}                 - White logo URL
{{COLOR_PRIMARY}}           - Primary hex color
{{COLOR_SECONDARY}}         - Secondary hex color
{{COLOR_ACCENT}}            - Accent hex color
```

### Services (4-6)
```
{{SERVICE_1_NAME}}          - Service 1 display name
{{SERVICE_1_SLUG}}          - Service 1 URL slug
{{SERVICE_2_NAME}}          - Service 2 display name
{{SERVICE_2_SLUG}}          - Service 2 URL slug
(etc.)
```

### Cities (1-5)
```
{{CITY_1_NAME}}             - City 1 name
{{CITY_1_SLUG}}             - City 1 URL slug
{{CITY_1_IMAGE}}            - City 1 card image
{{CITY_1_MAP_EMBED}}        - City 1 map iframe
{{CITY_1_META_DESC}}        - City 1 meta description
{{CITY_1_TS1_NAME}}         - City 1 Tourist Spot 1 name
{{CITY_1_TS1_IMAGE}}        - City 1 Tourist Spot 1 image
{{CITY_1_TS1_URL}}          - City 1 Tourist Spot 1 URL
(etc. for TS2, TS3, TTD1, TTD2, TTD3)
```

### Images
```
{{IMAGE_BG1}}, {{IMAGE_BG2}}, {{IMAGE_BG3}}     - Background images
{{IMAGE_HPL}}, {{IMAGE_HPP}}                     - Homepage images
{{IMAGE_SHARE}}                                   - OG/Social share image
{{IMAGE_S1L}}, {{IMAGE_S1P}}                     - Service 1 images
(etc. for S2, S3, S4)
```

### Hero Section
```
{{HERO_HEADLINE}}           - Main hero headline
{{HERO_SUBHEADING}}         - Hero subheading text
{{HERO_IMAGE}}              - Hero section image
{{HERO_CTA_PRIMARY_TEXT}}   - Primary CTA button text
{{HERO_CTA_PRIMARY_URL}}    - Primary CTA button URL
{{HERO_ADDRESS_DISPLAY}}    - Address shown in hero
```

### Tracking
```
GTM-PCG3NH9N        - GTM Container ID (e.g., GTM-XXXXXXX)
{{GA4_MEASUREMENT_ID}}      - GA4 ID (e.g., G-XXXXXXXXXX)
{{FB_PIXEL_ID}}             - Facebook Pixel ID
```

### Size Guide Units (1-16)
```
{{UNIT_1_SIZE}}             - Unit 1 size (e.g., 5'x5')
{{UNIT_1_SQFT}}             - Unit 1 square footage
{{UNIT_1_SHORT_DESC}}       - Unit 1 short description
{{UNIT_1_IMAGE}}            - Unit 1 image URL
{{UNIT_1_DESCRIPTION}}      - Unit 1 full description
{{UNIT_1_ITEMS}}            - What fits in unit 1
{{UNIT_1_ENABLED}}          - TRUE/FALSE to show unit
(etc.)
```

---

## Schema Markup Strategy

Each page type should have appropriate schema:

| Page | Schema Type |
|------|-------------|
| index.html | SelfStorage |
| about.html | Corporation |
| faqs.html | FAQPage |
| services/*.html | Service |
| cities/*.html | LocalBusiness + areaServed |

---

## Deployment Checklist

Before deploying:

1. [ ] All `{{PLACEHOLDER}}` values replaced
2. [ ] CSS colors updated in `_variables.css`
3. [ ] All images load correctly
4. [ ] GTM container ID is correct
5. [ ] StorEdge/booking embed works
6. [ ] Phone click-to-call works
7. [ ] Maps embed loads
8. [ ] Schema validates (use Google Rich Results Test)
9. [ ] Mobile menu works
10. [ ] All internal links work
11. [ ] sitemap.xml created with correct URLs
12. [ ] robots.txt has correct sitemap URL

---

## Netlify Deployment

1. Push to GitHub repository
2. Connect repository to Netlify
3. **IMPORTANT:** Clear the build command in Netlify UI (no build needed)
4. Set publish directory to `.` (root)
5. Deploy!

---

## CSS Customization

The only CSS file you typically need to edit is `css/_variables.css`:

1. Replace color placeholders with actual hex values
2. Generate color shade variants (50-950)
3. Optionally adjust fonts if brand requires different fonts

All other CSS files can remain unchanged.

---

## Notes

- This is a STATIC HTML site - no build step, no JavaScript framework
- Header and footer are duplicated in each file (no includes/partials)
- Mobile menu toggle is handled by `js/main.js`
- All images are hosted externally (S3, etc.) - URLs provided in Excel
- Legal pages (privacy, terms) should have `noindex, follow` robots directive
