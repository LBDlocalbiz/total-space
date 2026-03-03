"""Constants and required field definitions for the storage site generator."""

# Maximum supported counts
MAX_SERVICES = 6
MAX_CITIES = 5
MAX_UNITS = 16

# Required fields that must be present in Excel data
REQUIRED_FIELDS = [
    "BUSINESS_NAME",
    "DOMAIN",
    "PRIMARY_CITY",
    "STATE_CODE",
    "STATE_FULL",
    "ZIP_CODE",
    "STREET_ADDRESS",
    "PHONE_DISPLAY",
    "PHONE_TTC",
    "EMAIL_ADDRESS",
    "COLOR_PRIMARY",
    "COLOR_ACCENT",
    "LOGO_TR",
]

# Fields that are recommended but not required
RECOMMENDED_FIELDS = [
    "BRAND",
    "TAGLINE",
    "COMPANY_DESCRIPTION",
    "COLOR_SECONDARY",
    "LOGO_WH",
    "HOURS_DISPLAY",
    "HERO_HEADLINE",
    "HERO_SUBHEADING",
    "HERO_IMAGE",
    "HOME_META_DESC",
    "FACEBOOK_URL",
    "GB_MAP_SHARE",
    "GB_MAP_EMBED",
    "PAY_BILL_URL",
    "RENTAL_PORTAL_EMBED",
    "CURRENT_YEAR",
    "COUNTY_1",
    "LATITUDE",
    "LONGITUDE",
]

# Per-service required fields (X = service number)
SERVICE_FIELDS = [
    "SERVICE_{n}_NAME",
    "SERVICE_{n}_SLUG",
    "SERVICE_{n}_SHORT_DESC",
    "SERVICE_{n}_FULL_DESC",
    "SERVICE_{n}_META_DESC",
]

# Per-service optional fields
SERVICE_OPTIONAL_FIELDS = [
    "SERVICE_{n}_FEATURE_1",
    "SERVICE_{n}_FEATURE_2",
    "SERVICE_{n}_FEATURE_3",
    "SERVICE_{n}_FEATURE_4",
]

# Per-city required fields (X = city number)
CITY_FIELDS = [
    "CITY_{n}_NAME",
    "CITY_{n}_SLUG",
    "CITY_{n}_IMAGE",
    "CITY_{n}_META_DESC",
    "CITY_{n}_FULL_DESC",
    "CITY_{n}_MAP_EMBED",
]

# Per-city optional fields (tourist spots and things to do)
CITY_OPTIONAL_FIELDS = [
    "CITY_{n}_TS1_NAME", "CITY_{n}_TS1_IMAGE", "CITY_{n}_TS1_URL",
    "CITY_{n}_TS2_NAME", "CITY_{n}_TS2_IMAGE", "CITY_{n}_TS2_URL",
    "CITY_{n}_TS3_NAME", "CITY_{n}_TS3_IMAGE", "CITY_{n}_TS3_URL",
    "CITY_{n}_TTD1_NAME", "CITY_{n}_TTD1_IMAGE", "CITY_{n}_TTD1_URL",
    "CITY_{n}_TTD2_NAME", "CITY_{n}_TTD2_IMAGE", "CITY_{n}_TTD2_URL",
    "CITY_{n}_TTD3_NAME", "CITY_{n}_TTD3_IMAGE", "CITY_{n}_TTD3_URL",
]

# Per-unit fields
UNIT_FIELDS = [
    "UNIT_{n}_SIZE",
    "UNIT_{n}_SQFT",
    "UNIT_{n}_SHORT_DESC",
    "UNIT_{n}_DESCRIPTION",
    "UNIT_{n}_ITEMS",
    "UNIT_{n}_ENABLED",
    "UNIT_{n}_IMAGE",
]

# Tracking fields from Tracking & Schema sheet
TRACKING_FIELDS = [
    "GTM_CONTAINER_ID",
    "GTM_HEAD_CODE",
    "GTM_BODY_CODE",
    "GA4_MEASUREMENT_ID",
]

# Core HTML pages that get simple placeholder replacement
CORE_PAGES = [
    "index.html",
    "about.html",
    "contact.html",
    "size-guide.html",
    "faqs.html",
    "privacy.html",
    "terms.html",
    "404.html",
]

# Service icon SVGs (reused across templates)
SERVICE_ICONS = [
    # Icon 1: Building/Storage
    '<svg class="wss-service-card__icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>',
    # Icon 2: Climate/Chart
    '<svg class="wss-service-card__icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>',
    # Icon 3: Vehicle/Car
    '<svg class="wss-service-card__icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7h8m-8 5h8m-4 8V10m-6 10h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>',
    # Icon 4: Boat/RV/Trailer
    '<svg class="wss-service-card__icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 17h.01M17 17h.01M3 11h18M5 17h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2zm0 0v2m14-2v2M7 11V7m10 4V7"/></svg>',
    # Icon 5: Business/Briefcase
    '<svg class="wss-service-card__icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>',
    # Icon 6: Records/Document
    '<svg class="wss-service-card__icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>',
]

# Hardcoded GTM ID in templates that needs to be replaced
TEMPLATE_GTM_ID = "GTM-PCG3NH9N"

# Default color for secondary if not provided
DEFAULT_SECONDARY_COLOR = "#FFFFFF"
