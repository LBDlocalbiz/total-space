"""Main site generation module.

Orchestrates building the complete static HTML website from templates and
Excel data. Handles dynamic section rebuilding for varying service/city counts,
footer service links, blog integration, and LLM-Index linking.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict

from .constants import CORE_PAGES, SERVICE_ICONS, MAX_SERVICES, MAX_CITIES, DEFAULT_SECONDARY_COLOR
from .excel_reader import get_service_count, get_city_count, get_enabled_units
from .color_utils import generate_variables_css
from .placeholder_engine import (
    process_file,
    replace_service_x,
    replace_city_x,
    replace_placeholders,
    replace_gtm,
    find_unreplaced,
)
from .sitemap_builder import build_sitemap


# ---------------------------------------------------------------------------
# Helper: Footer service links
# ---------------------------------------------------------------------------

def _build_footer_services_html(data: dict) -> str:
    """Build the footer Our Services <ul> inner HTML.

    Generates one <li> per active service using the service slug and name
    from the data dictionary.
    """
    service_count = get_service_count(data)
    items = []
    for n in range(1, service_count + 1):
        slug = data.get(f"SERVICE_{n}_SLUG", "")
        name = data.get(f"SERVICE_{n}_NAME", "")
        if slug and name:
            items.append(
                f'<li><a href="/services/{slug}.html" '
                f'class="wss-footer__nav-link">{name}</a></li>'
            )
    return "".join(items)


def _fix_footer_services(content: str, data: dict) -> str:
    """Replace the hardcoded footer services section with dynamic one.

    Locates the footer column with heading "Our Services" and replaces
    the inner <ul> content with dynamically generated service links.
    """
    new_items = _build_footer_services_html(data)

    # Pattern: find the Our Services heading followed by the <ul> block
    pattern = (
        r'(<h3 class="wss-footer__heading">Our Services</h3>'
        r'<ul class="wss-footer__nav">)'
        r'(.*?)'
        r'(</ul></div>)'
    )
    replacement = rf'\g<1>{new_items}\g<3>'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    return content


# ---------------------------------------------------------------------------
# Helper: LLM-Index and Blog links
# ---------------------------------------------------------------------------

def _add_llm_index_link(content: str) -> str:
    """Add <link rel="llm-index"> before </head>."""
    link_tag = '<link rel="llm-index" href="/llm-index.json" type="application/json">'
    if link_tag in content:
        return content
    return content.replace("</head>", f"  {link_tag}\n</head>")


def _add_blog_link_to_footer(content: str, blog_domain: str) -> str:
    """Add Blog link to footer Quick Links section.

    Inserts a Blog link as the last item in the Quick Links <ul>.
    Only adds it if a blog_domain is provided and the link isn't already present.
    """
    if not blog_domain:
        return content
    blog_domain = blog_domain.rstrip("/")
    blog_link = (
        f'<li><a href="{blog_domain}/" class="wss-footer__nav-link" '
        f'target="_blank" rel="noopener noreferrer">Blog</a></li>'
    )
    # Find the Quick Links <ul> and insert before its closing tag
    pattern = (
        r'(<h3 class="wss-footer__heading">Quick Links</h3>'
        r'<ul class="wss-footer__nav">)'
        r'(.*?)'
        r'(</ul></div>)'
    )
    match = re.search(pattern, content, flags=re.DOTALL)
    if match and "Blog</a></li>" not in match.group(2):
        existing_items = match.group(2)
        new_block = f"{match.group(1)}{existing_items}{blog_link}{match.group(3)}"
        content = content[:match.start()] + new_block + content[match.end():]
    return content


# ---------------------------------------------------------------------------
# Helper: Service cards
# ---------------------------------------------------------------------------

def _build_service_cards_html(data: dict, exclude_service: int = 0) -> str:
    """Build service cards HTML for services/index.html or 'Other Services' sections.

    Args:
        data: Site data dictionary.
        exclude_service: Service number to exclude (for "Other Services" sections).
                         0 means include all services.

    Returns:
        HTML string of service card <a> elements.
    """
    service_count = get_service_count(data)
    cards = []
    for n in range(1, service_count + 1):
        if n == exclude_service:
            continue
        slug = data.get(f"SERVICE_{n}_SLUG", "")
        name = data.get(f"SERVICE_{n}_NAME", "")
        icon_idx = min(n - 1, len(SERVICE_ICONS) - 1)
        icon = SERVICE_ICONS[icon_idx]
        cards.append(
            f'<a href="/services/{slug}.html" class="wss-service-card">'
            f'<div class="wss-service-card__icon-wrapper">{icon}</div>'
            f'<h3 class="wss-service-card__title">{name}</h3>'
            f'<span class="wss-service-card__link">Learn More '
            f'<svg class="wss-service-card__link-icon" fill="none" stroke="currentColor" '
            f'viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" '
            f'stroke-width="2" d="M9 5l7 7-7 7"/></svg></span></a>'
        )
    return "\n        ".join(cards)


def _build_services_index_cards_html(data: dict) -> str:
    """Build the large service cards for services/index.html.

    Uses the --large card variant with background images and short descriptions.
    """
    service_count = get_service_count(data)
    cards = []
    for n in range(1, service_count + 1):
        slug = data.get(f"SERVICE_{n}_SLUG", "")
        name = data.get(f"SERVICE_{n}_NAME", "")
        short_desc = data.get(f"SERVICE_{n}_SHORT_DESC", "")
        image = data.get(f"IMAGE_S{n}L", "")
        cards.append(
            f'\n        <!-- SERVICE {n} -->\n'
            f'        <a href="/services/{slug}.html" class="wss-service-card wss-service-card--large">\n'
            f'          <img src="{image}" alt="{name}" class="wss-service-card__bg-image">\n'
            f'          <div class="wss-service-card__overlay"></div>\n'
            f'          <div class="wss-service-card__content">\n'
            f'            <h3 class="wss-service-card__title">{name}</h3>\n'
            f'            <p class="wss-service-card__description">{short_desc}</p>\n'
            f'            <span class="wss-service-card__link">Learn More '
            f'<svg class="wss-service-card__link-icon" fill="none" stroke="currentColor" '
            f'viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" '
            f'stroke-width="2" d="M9 5l7 7-7 7"/></svg></span>\n'
            f'          </div>\n'
            f'        </a>'
        )
    return "".join(cards)


# ---------------------------------------------------------------------------
# Helper: City cards
# ---------------------------------------------------------------------------

def _build_city_cards_html(data: dict, exclude_city: int = 0) -> str:
    """Build city cards HTML for cities/index.html or 'Other Areas' sections.

    Args:
        data: Site data dictionary.
        exclude_city: City number to exclude (for "Other Areas" sections).
                      0 means include all cities.

    Returns:
        HTML string of area card <a> elements.
    """
    city_count = get_city_count(data)
    state_code = data.get("STATE_CODE", "")
    cards = []
    for n in range(1, city_count + 1):
        if n == exclude_city:
            continue
        slug = data.get(f"CITY_{n}_SLUG", "")
        name = data.get(f"CITY_{n}_NAME", "")
        image = data.get(f"CITY_{n}_IMAGE", "")
        cards.append(
            f'<a href="/cities/{slug}.html" class="wss-area-card">'
            f'<img src="{image}" alt="Storage near {name}, {state_code}" '
            f'class="wss-area-card__image">'
            f'<div class="wss-area-card__overlay"></div>'
            f'<div class="wss-area-card__content">'
            f'<h3 class="wss-area-card__title">{name}</h3>'
            f'<p class="wss-area-card__state">{state_code}</p>'
            f'</div></a>'
        )
    return "\n        ".join(cards)


def _build_cities_index_cards_html(data: dict) -> str:
    """Build the large city cards for cities/index.html.

    Uses the --large card variant with state code and link text.
    """
    city_count = get_city_count(data)
    state_code = data.get("STATE_CODE", "")
    cards = []
    for n in range(1, city_count + 1):
        slug = data.get(f"CITY_{n}_SLUG", "")
        name = data.get(f"CITY_{n}_NAME", "")
        image = data.get(f"CITY_{n}_IMAGE", "")
        cards.append(
            f'\n        <!-- CITY {n} -->\n'
            f'        <a href="/cities/{slug}.html" class="wss-area-card wss-area-card--large">\n'
            f'          <img src="{image}" alt="Storage near {name}, {state_code}" '
            f'class="wss-area-card__image">\n'
            f'          <div class="wss-area-card__overlay"></div>\n'
            f'          <div class="wss-area-card__content">\n'
            f'            <h3 class="wss-area-card__title">{name}</h3>\n'
            f'            <p class="wss-area-card__state">{state_code}</p>\n'
            f'            <span class="wss-area-card__link">View Storage Options &rarr;</span>\n'
            f'          </div>\n'
            f'        </a>'
        )
    return "".join(cards)


# ---------------------------------------------------------------------------
# Helper: Grid class for count
# ---------------------------------------------------------------------------

def _grid_class_for_count(count: int, context: str = "default") -> str:
    """Determine the appropriate wss-grid--N class for an item count.

    Args:
        count: Number of items in the grid.
        context: 'cities-index' for cities/index.html, 'homepage-cities'
                 for homepage area cards, or 'default'.

    Returns:
        CSS grid class like 'wss-grid--3'.
    """
    if count <= 1:
        return "wss-grid--1"
    elif count == 2:
        return "wss-grid--2"
    elif count == 3:
        return "wss-grid--3"
    elif count == 4:
        return "wss-grid--2"
    elif count == 5:
        if context in ("homepage-cities",):
            return "wss-grid--5"
        return "wss-grid--3"
    else:
        return "wss-grid--3"


# ---------------------------------------------------------------------------
# Helper: Homepage dynamic sections
# ---------------------------------------------------------------------------

def _build_homepage_service_cards(data: dict) -> str:
    """Build homepage service cards section.

    Each card is an <a> tag with icon, title, description placeholder, and
    "Learn More" link, matching the homepage template pattern.
    """
    service_count = get_service_count(data)
    cards = []
    for n in range(1, service_count + 1):
        slug = data.get(f"SERVICE_{n}_SLUG", "")
        name = data.get(f"SERVICE_{n}_NAME", "")
        short_desc = data.get(f"SERVICE_{n}_SHORT_DESC", "")
        icon_idx = min(n - 1, len(SERVICE_ICONS) - 1)
        icon = SERVICE_ICONS[icon_idx]
        cards.append(
            f'\n        <!-- SERVICE {n} -->\n'
            f'        <a href="/services/{slug}.html" class="wss-service-card">'
            f'<div class="wss-service-card__icon-wrapper">{icon}</div>'
            f'<h3 class="wss-service-card__title">{name}</h3>'
            f'<p class="wss-service-card__description">{short_desc}</p>'
            f'<span class="wss-service-card__link">Learn More '
            f'<svg class="wss-service-card__link-icon" fill="none" stroke="currentColor" '
            f'viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" '
            f'stroke-width="2" d="M9 5l7 7-7 7"/></svg></span></a>'
        )
    return "".join(cards)


def _build_homepage_city_cards(data: dict) -> str:
    """Build homepage city area cards section."""
    city_count = get_city_count(data)
    state_code = data.get("STATE_CODE", "")
    cards = []
    for n in range(1, city_count + 1):
        slug = data.get(f"CITY_{n}_SLUG", "")
        name = data.get(f"CITY_{n}_NAME", "")
        image = data.get(f"CITY_{n}_IMAGE", "")
        cards.append(
            f'\n        <a href="/cities/{slug}.html" class="wss-area-card">'
            f'<img src="{image}" alt="Storage near {name}, {state_code}" '
            f'class="wss-area-card__image">'
            f'<div class="wss-area-card__overlay"></div>'
            f'<div class="wss-area-card__content">'
            f'<h3 class="wss-area-card__title">{name}</h3>'
            f'<p class="wss-area-card__state">{state_code}</p>'
            f'</div></a>'
        )
    return "".join(cards)


def _build_schema_area_served(data: dict) -> str:
    """Build the areaServed.containsPlace JSON array for homepage schema.

    Generates the JSON array of City objects from actual city data,
    replacing the hardcoded 5-city template block.
    """
    city_count = get_city_count(data)
    state_full = data.get("STATE_FULL", "")
    places = []
    for n in range(1, city_count + 1):
        name = data.get(f"CITY_{n}_NAME", "")
        if name:
            places.append(f'{{"@type": "City", "name": "{name}, {state_full}"}}')
    return "[\n        " + ",\n        ".join(places) + "\n      ]"


# ---------------------------------------------------------------------------
# Helper: City page - Storage Options Available
# ---------------------------------------------------------------------------

def _build_city_service_links(data: dict) -> str:
    """Build the 'Storage Options Available' service links for city pages.

    Generates a grid of service links matching the city template pattern.
    """
    service_count = get_service_count(data)
    links = []
    for n in range(1, service_count + 1):
        slug = data.get(f"SERVICE_{n}_SLUG", "")
        name = data.get(f"SERVICE_{n}_NAME", "")
        links.append(
            f'<a href="/services/{slug}.html" style="display: flex; align-items: center; '
            f'padding: 1rem; background: var(--wss-gray-50); border-radius: 0.5rem; '
            f'text-decoration: none; color: inherit; transition: background 0.2s;">\n'
            f'              <svg style="width: 1.5rem; height: 1.5rem; color: var(--wss-primary); '
            f'margin-right: 0.75rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
            f'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" '
            f'd="M5 13l4 4L19 7"/></svg>\n'
            f'              <span style="font-weight: 500;">{name}</span>\n'
            f'            </a>'
        )
    return "\n            ".join(links)


# ---------------------------------------------------------------------------
# Helper: robots.txt
# ---------------------------------------------------------------------------

def _build_robots_txt(data: dict) -> str:
    """Generate robots.txt content with correct domain, sitemap, and LLM directives."""
    domain = data.get("DOMAIN", "https://example.com/").rstrip("/")
    return (
        f"User-agent: *\n"
        f"Allow: /\n"
        f"\n"
        f"# Disallow admin and non-public pages\n"
        f"Disallow: /404.html\n"
        f"\n"
        f"# Sitemap location\n"
        f"Sitemap: {domain}/sitemap.xml\n"
        f"\n"
        f"# LLM-Index for AI assistants\n"
        f"LLM-Index: {domain}/llm-index.json\n"
    )


# ---------------------------------------------------------------------------
# Helper: Apply all common post-processing to a page
# ---------------------------------------------------------------------------

def _postprocess_page(content: str, data: dict, blog_domain: str = "") -> str:
    """Apply footer fix, LLM-Index link, and blog link to a processed page."""
    content = _fix_footer_services(content, data)
    content = _add_llm_index_link(content)
    if blog_domain:
        content = _add_blog_link_to_footer(content, blog_domain)
    return content


# ---------------------------------------------------------------------------
# Homepage rebuilding
# ---------------------------------------------------------------------------

def _rebuild_homepage_services_section(content: str, data: dict) -> str:
    """Rebuild the homepage services grid with the actual number of services.

    Finds the services section grid (between the SERVICE 1 comment and the
    closing </div> of the wss-grid) and replaces with dynamic cards.
    """
    service_count = get_service_count(data)
    grid_class = _grid_class_for_count(service_count)

    # Pattern: the grid div containing service cards in the services section
    pattern = (
        r'(<div class="wss-grid wss-grid--3" style="gap: 1\.5rem;">\s*'
        r'<!-- SERVICE 1 -->)'
        r'(.*?)'
        r'(</div>\s*</div>\s*</section>\s*'
        r'<!-- AREAS SECTION -->)'
    )
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        new_cards = _build_homepage_service_cards(data)
        new_grid = (
            f'<div class="wss-grid {grid_class}" style="gap: 1.5rem;">'
            f'{new_cards}\n      </div>\n    </div>\n  </section>\n\n'
            f'  <!-- AREAS SECTION -->'
        )
        content = content[:match.start()] + new_grid + content[match.end():]

    return content


def _rebuild_homepage_areas_section(content: str, data: dict) -> str:
    """Rebuild the homepage areas grid with the actual number of cities."""
    city_count = get_city_count(data)
    grid_class = _grid_class_for_count(city_count, context="homepage-cities")

    # Pattern: the areas grid div
    pattern = (
        r'<div class="wss-grid wss-grid--5" style="gap: 1\.5rem;">'
        r'(.*?)'
        r'</div>\s*<div class="wss-text-center wss-mt-8">'
    )
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        new_cards = _build_homepage_city_cards(data)
        replacement = (
            f'<div class="wss-grid {grid_class}" style="gap: 1.5rem;">'
            f'{new_cards}\n      </div>\n      <div class="wss-text-center wss-mt-8">'
        )
        content = content[:match.start()] + replacement + content[match.end():]

    return content


def _rebuild_homepage_schema_area_served(content: str, data: dict) -> str:
    """Replace the hardcoded 5-city areaServed.containsPlace in the homepage schema."""
    # Pattern matches the containsPlace array in the schema JSON
    pattern = (
        r'("containsPlace":\s*\[)'
        r'(.*?)'
        r'(\]\s*\})'
    )
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        new_places = _build_schema_area_served(data)
        # Replace the entire containsPlace block
        full_pattern = r'"containsPlace":\s*\[.*?\]'
        content = re.sub(
            full_pattern,
            f'"containsPlace": {new_places}',
            content,
            count=1,
            flags=re.DOTALL,
        )

    return content


# ---------------------------------------------------------------------------
# Service pages: rebuild "Other Services" section
# ---------------------------------------------------------------------------

def _rebuild_other_services(content: str, data: dict, current_service: int) -> str:
    """Rebuild the 'Other Services' section to exclude the current service.

    Finds the grid after the "Other Storage Services" heading and replaces
    with cards for all services except the current one.
    """
    service_count = get_service_count(data)
    other_count = service_count - 1
    if other_count < 1:
        # Only one service -- remove the entire Other Services section
        pattern = (
            r'<!-- OTHER SERVICES -->.*?'
            r'(?=<!-- CTA SECTION -->)'
        )
        content = re.sub(pattern, "", content, flags=re.DOTALL)
        return content

    grid_class = _grid_class_for_count(other_count)
    new_cards = _build_service_cards_html(data, exclude_service=current_service)

    # Pattern: find the grid in the Other Services section
    pattern = (
        r'(<div class="wss-grid wss-grid--)\d+(">\s*)'
        r'(<!-- Show other services.*?)'
        r'(</div>\s*</div>\s*</section>\s*'
        r'<!-- CTA SECTION -->)'
    )
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        replacement = (
            f'{match.group(1)}{grid_class.split("--")[1]}{match.group(2)}'
            f'{new_cards}\n      '
            f'{match.group(4)}'
        )
        content = content[:match.start()] + replacement + content[match.end():]
    else:
        # Fallback: try a simpler pattern without the comment
        pattern2 = (
            r'(Other Storage Services</h2>\s*</div>\s*)'
            r'<div class="wss-grid wss-grid--\d+">'
            r'(.*?)'
            r'(</div>\s*</div>\s*</section>\s*<!-- CTA SECTION -->)'
        )
        match2 = re.search(pattern2, content, flags=re.DOTALL)
        if match2:
            replacement = (
                f'{match2.group(1)}'
                f'<div class="wss-grid {grid_class}">\n'
                f'        {new_cards}\n      '
                f'{match2.group(3)}'
            )
            content = content[:match2.start()] + replacement + content[match2.end():]

    return content


# ---------------------------------------------------------------------------
# City pages: rebuild "Other Areas" section
# ---------------------------------------------------------------------------

def _rebuild_other_areas(content: str, data: dict, current_city: int) -> str:
    """Rebuild the 'Other Areas We Serve' section to exclude the current city."""
    city_count = get_city_count(data)
    other_count = city_count - 1
    if other_count < 1:
        # Only one city -- remove the Other Areas section
        pattern = (
            r'<!-- OTHER AREAS -->.*?'
            r'(?=<!-- CTA SECTION -->)'
        )
        content = re.sub(pattern, "", content, flags=re.DOTALL)
        return content

    grid_class = _grid_class_for_count(other_count)
    new_cards = _build_city_cards_html(data, exclude_city=current_city)

    # Pattern: find the grid in the Other Areas section
    pattern = (
        r'(Other Areas We Serve</h2>\s*</div>\s*)'
        r'<div class="wss-grid wss-grid--\d+">'
        r'(.*?)'
        r'(</div>\s*</div>\s*</section>\s*<!-- CTA SECTION -->)'
    )
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        replacement = (
            f'{match.group(1)}'
            f'<div class="wss-grid {grid_class}">\n'
            f'        {new_cards}\n      '
            f'{match.group(3)}'
        )
        content = content[:match.start()] + replacement + content[match.end():]

    return content


# ---------------------------------------------------------------------------
# City pages: rebuild "Storage Options Available" section
# ---------------------------------------------------------------------------

def _rebuild_city_service_options(content: str, data: dict) -> str:
    """Rebuild the 'Storage Options Available' grid in city pages.

    Replaces the hardcoded 4-service links with the actual services.
    """
    service_count = get_service_count(data)
    grid_class = _grid_class_for_count(service_count)
    new_links = _build_city_service_links(data)

    # Pattern: the grid div after "Storage Options Available" heading
    pattern = (
        r'(Storage Options Available</h3>\s*)'
        r'<div class="wss-grid wss-grid--\d+"[^>]*>'
        r'(.*?)'
        r'(</div>\s*<div style="margin-top: 2rem;")'
    )
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        replacement = (
            f'{match.group(1)}'
            f'<div class="wss-grid {grid_class}" style="gap: 1rem;">\n'
            f'            {new_links}\n'
            f'          {match.group(3)}'
        )
        content = content[:match.start()] + replacement + content[match.end():]

    return content


# ---------------------------------------------------------------------------
# Services index: rebuild service cards
# ---------------------------------------------------------------------------

def _rebuild_services_index(content: str, data: dict) -> str:
    """Rebuild the services/index.html page with actual service count."""
    service_count = get_service_count(data)
    grid_class = _grid_class_for_count(service_count)
    new_cards = _build_services_index_cards_html(data)

    # Pattern: the grid div containing service cards
    pattern = (
        r'(<div class="wss-grid wss-grid--2" style="gap: 2rem;">\s*'
        r'<!-- SERVICE 1 -->)'
        r'(.*?)'
        r'(</div>\s*</div>\s*</section>\s*'
        r'<!-- WHY CHOOSE US -->)'
    )
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        replacement = (
            f'<div class="wss-grid {grid_class}" style="gap: 2rem;">'
            f'{new_cards}\n      </div>\n    </div>\n  </section>\n\n'
            f'  <!-- WHY CHOOSE US -->'
        )
        content = content[:match.start()] + replacement + content[match.end():]

    return content


# ---------------------------------------------------------------------------
# Cities index: rebuild city cards
# ---------------------------------------------------------------------------

def _rebuild_cities_index(content: str, data: dict) -> str:
    """Rebuild the cities/index.html page with actual city count."""
    city_count = get_city_count(data)
    grid_class = _grid_class_for_count(city_count, context="cities-index")
    new_cards = _build_cities_index_cards_html(data)

    # Pattern: the grid div containing city cards
    pattern = (
        r'(<div class="wss-grid wss-grid--3" style="gap: 2rem;">\s*'
        r'<!-- CITY 1 -->)'
        r'(.*?)'
        r'(</div>\s*</div>\s*</section>\s*'
        r'<!-- MAP SECTION -->)'
    )
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        replacement = (
            f'<div class="wss-grid {grid_class}" style="gap: 2rem;">'
            f'{new_cards}\n      </div>\n    </div>\n  </section>\n\n'
            f'  <!-- MAP SECTION -->'
        )
        content = content[:match.start()] + replacement + content[match.end():]

    return content


# ===========================================================================
# Main build function
# ===========================================================================

def build_main_site(
    data: dict,
    template_dir: str,
    output_dir: str,
    blog_domain: str = "",
) -> dict:
    """Build the complete static HTML website from templates and data.

    Args:
        data: Flat dictionary of placeholder keys to values (from Excel).
        template_dir: Path to the main template directory.
        output_dir: Path where the generated site will be written.
        blog_domain: Optional blog domain (e.g., "https://blog.example.com").

    Returns:
        Summary dict with generation statistics including page counts and
        lists of generated files.
    """
    template_path = Path(template_dir)
    output_path = Path(output_dir)

    service_count = get_service_count(data)
    city_count = get_city_count(data)

    pages_generated = []
    warnings = []

    print(f"Building main site: {service_count} services, {city_count} cities")

    # ------------------------------------------------------------------
    # 1. Setup output directory
    # ------------------------------------------------------------------
    for subdir in ["css", "js", "services", "cities"]:
        os.makedirs(output_path / subdir, exist_ok=True)
    print("  Created output directories")

    # ------------------------------------------------------------------
    # 2. Generate _variables.css
    # ------------------------------------------------------------------
    primary = data.get("COLOR_PRIMARY", "#1a365d")
    secondary = data.get("COLOR_SECONDARY", DEFAULT_SECONDARY_COLOR)
    accent = data.get("COLOR_ACCENT", "#f59e0b")

    variables_css = generate_variables_css(primary, secondary, accent)
    (output_path / "css" / "_variables.css").write_text(variables_css, encoding="utf-8")
    print("  Generated css/_variables.css")

    # ------------------------------------------------------------------
    # 3. Copy static CSS/JS files
    # ------------------------------------------------------------------
    css_src = template_path / "css"
    if css_src.is_dir():
        for css_file in css_src.iterdir():
            if css_file.is_file() and css_file.name != "_variables.css":
                shutil.copy2(str(css_file), str(output_path / "css" / css_file.name))

    js_src = template_path / "js"
    if js_src.is_dir():
        for js_file in js_src.iterdir():
            if js_file.is_file():
                shutil.copy2(str(js_file), str(output_path / "js" / js_file.name))

    print("  Copied static CSS and JS files")

    # ------------------------------------------------------------------
    # 4. Process core HTML pages
    # ------------------------------------------------------------------
    for page in CORE_PAGES:
        src_file = template_path / page
        if not src_file.exists():
            warnings.append(f"Template missing: {page}")
            continue

        content = src_file.read_text(encoding="utf-8")
        content = process_file(content, data)

        # Special handling for index.html (homepage)
        if page == "index.html":
            content = _rebuild_homepage_services_section(content, data)
            content = _rebuild_homepage_areas_section(content, data)
            content = _rebuild_homepage_schema_area_served(content, data)

        content = _postprocess_page(content, data, blog_domain)
        (output_path / page).write_text(content, encoding="utf-8")
        pages_generated.append(page)
        print(f"  Generated {page}")

    # ------------------------------------------------------------------
    # 5. Generate service pages
    # ------------------------------------------------------------------
    service_template_file = template_path / "services" / "_service-template.html"
    if service_template_file.exists():
        service_template = service_template_file.read_text(encoding="utf-8")

        for n in range(1, service_count + 1):
            content = service_template
            # Replace SERVICE_X placeholders with SERVICE_N values
            content = replace_service_x(content, n, data)
            # Process remaining placeholders and GTM
            content = process_file(content, data)
            # Rebuild "Other Services" section
            content = _rebuild_other_services(content, data, current_service=n)
            # Apply post-processing
            content = _postprocess_page(content, data, blog_domain)

            slug = data.get(f"SERVICE_{n}_SLUG", f"service-{n}")
            out_file = f"services/{slug}.html"
            (output_path / out_file).write_text(content, encoding="utf-8")
            pages_generated.append(out_file)
            print(f"  Generated {out_file}")
    else:
        warnings.append("Template missing: services/_service-template.html")

    # ------------------------------------------------------------------
    # 6. Generate services/index.html
    # ------------------------------------------------------------------
    services_index_file = template_path / "services" / "index.html"
    if services_index_file.exists():
        content = services_index_file.read_text(encoding="utf-8")
        content = process_file(content, data)
        content = _rebuild_services_index(content, data)
        content = _postprocess_page(content, data, blog_domain)
        (output_path / "services" / "index.html").write_text(content, encoding="utf-8")
        pages_generated.append("services/index.html")
        print("  Generated services/index.html")
    else:
        warnings.append("Template missing: services/index.html")

    # ------------------------------------------------------------------
    # 7. Generate city pages
    # ------------------------------------------------------------------
    city_template_file = template_path / "cities" / "_city-template.html"
    if city_template_file.exists():
        city_template = city_template_file.read_text(encoding="utf-8")

        for n in range(1, city_count + 1):
            content = city_template
            # Replace CITY_X placeholders with CITY_N values
            content = replace_city_x(content, n, data)
            # Process remaining placeholders and GTM
            content = process_file(content, data)
            # Rebuild dynamic sections
            content = _rebuild_other_areas(content, data, current_city=n)
            content = _rebuild_city_service_options(content, data)
            # Apply post-processing
            content = _postprocess_page(content, data, blog_domain)

            slug = data.get(f"CITY_{n}_SLUG", f"city-{n}")
            out_file = f"cities/{slug}.html"
            (output_path / out_file).write_text(content, encoding="utf-8")
            pages_generated.append(out_file)
            print(f"  Generated {out_file}")
    else:
        warnings.append("Template missing: cities/_city-template.html")

    # ------------------------------------------------------------------
    # 8. Generate cities/index.html
    # ------------------------------------------------------------------
    cities_index_file = template_path / "cities" / "index.html"
    if cities_index_file.exists():
        content = cities_index_file.read_text(encoding="utf-8")
        content = process_file(content, data)
        content = _rebuild_cities_index(content, data)
        content = _postprocess_page(content, data, blog_domain)
        (output_path / "cities" / "index.html").write_text(content, encoding="utf-8")
        pages_generated.append("cities/index.html")
        print("  Generated cities/index.html")
    else:
        warnings.append("Template missing: cities/index.html")

    # ------------------------------------------------------------------
    # 9. Generate sitemap.xml
    # ------------------------------------------------------------------
    sitemap_content = build_sitemap(data)
    (output_path / "sitemap.xml").write_text(sitemap_content, encoding="utf-8")
    pages_generated.append("sitemap.xml")
    print("  Generated sitemap.xml")

    # ------------------------------------------------------------------
    # 10. Generate robots.txt
    # ------------------------------------------------------------------
    robots_content = _build_robots_txt(data)
    (output_path / "robots.txt").write_text(robots_content, encoding="utf-8")
    pages_generated.append("robots.txt")
    print("  Generated robots.txt")

    # ------------------------------------------------------------------
    # 11. Generate netlify.toml
    # ------------------------------------------------------------------
    netlify_template = template_path / "netlify.toml"
    if netlify_template.exists():
        content = netlify_template.read_text(encoding="utf-8")
        content = process_file(content, data)
        (output_path / "netlify.toml").write_text(content, encoding="utf-8")
        pages_generated.append("netlify.toml")
        print("  Generated netlify.toml")
    else:
        warnings.append("Template missing: netlify.toml")

    # ------------------------------------------------------------------
    # 12. Generate _redirects
    # ------------------------------------------------------------------
    redirects_template = template_path / "_redirects"
    if redirects_template.exists():
        content = redirects_template.read_text(encoding="utf-8")
        content = process_file(content, data)
        (output_path / "_redirects").write_text(content, encoding="utf-8")
        pages_generated.append("_redirects")
        print("  Generated _redirects")
    else:
        warnings.append("Template missing: _redirects")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    summary = {
        "total_pages": len(pages_generated),
        "core_pages": len([p for p in pages_generated if "/" not in p and p.endswith(".html")]),
        "service_pages": len([p for p in pages_generated if p.startswith("services/")]),
        "city_pages": len([p for p in pages_generated if p.startswith("cities/")]),
        "service_count": service_count,
        "city_count": city_count,
        "pages_generated": pages_generated,
        "warnings": warnings,
    }

    print(f"\nBuild complete: {summary['total_pages']} files generated")
    if warnings:
        print(f"  Warnings: {len(warnings)}")
        for w in warnings:
            print(f"    - {w}")

    return summary
