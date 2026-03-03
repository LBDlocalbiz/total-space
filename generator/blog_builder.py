"""Generate the blog site from templates and Excel data."""

import os
import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Dict

from .constants import DEFAULT_SECONDARY_COLOR
from .color_utils import generate_variables_css
from .excel_reader import get_service_count
from .placeholder_engine import replace_placeholders, replace_gtm
from .sitemap_builder import build_blog_sitemap


def build_blog(data: Dict[str, str], template_dir: str, output_dir: str,
               blog_domain: str = "", main_domain: str = "") -> Dict:
    """Build the blog site.

    Args:
        data: Placeholder data dictionary
        template_dir: Path to templates/blog/
        output_dir: Path to write blog output
        blog_domain: Full blog domain (e.g. https://blog.example.com)
        main_domain: Full main site domain (e.g. https://example.com)

    Returns:
        Summary dict with stats.
    """
    template_path = Path(template_dir)
    output_path = Path(output_dir)

    # Derive domains
    if not main_domain:
        main_domain = data.get("DOMAIN", "https://example.com/").rstrip("/")
    main_domain = main_domain.rstrip("/")

    if not blog_domain:
        # Default: blog.{domain without https://}
        domain_bare = main_domain.replace("https://", "").replace("http://", "")
        blog_domain = f"https://blog.{domain_bare}"
    blog_domain = blog_domain.rstrip("/")

    # Create output dirs
    os.makedirs(output_path / "css", exist_ok=True)
    os.makedirs(output_path / "js", exist_ok=True)
    os.makedirs(output_path / "posts", exist_ok=True)

    stats = {"pages": 0, "posts": 0}

    # 1. Generate _variables.css (same colors as main site)
    primary = data.get("COLOR_PRIMARY", "#1E3A5F")
    secondary = data.get("COLOR_SECONDARY", DEFAULT_SECONDARY_COLOR)
    accent = data.get("COLOR_ACCENT", "#C41E3A")
    css_content = generate_variables_css(primary, secondary, accent)
    _write(output_path / "css" / "_variables.css", css_content)

    # 2. Copy other CSS/JS files from template
    for css_file in (template_path / "css").glob("*"):
        if css_file.name != "_variables.css":
            shutil.copy2(str(css_file), str(output_path / "css" / css_file.name))

    for js_file in (template_path / "js").glob("*"):
        shutil.copy2(str(js_file), str(output_path / "js" / js_file.name))

    # 3. Generate blog index.html
    business_name = data.get("BUSINESS_NAME", "Self Storage")
    primary_city = data.get("PRIMARY_CITY", "")
    state_code = data.get("STATE_CODE", "")
    phone_display = data.get("PHONE_DISPLAY", "")
    phone_ttc = data.get("PHONE_TTC", "")
    tagline = data.get("TAGLINE", f"Secure, affordable self storage in {primary_city}, {state_code}.")
    logo = data.get("LOGO_TR", "")
    pay_bill_url = data.get("PAY_BILL_URL", "#")
    facebook_url = data.get("FACEBOOK_URL", "#")
    gb_map = data.get("GB_MAP_SHARE", "#")
    email = data.get("EMAIL_ADDRESS", "")
    street = data.get("STREET_ADDRESS", "")
    zip_code = data.get("ZIP_CODE", "")
    gtm_id = data.get("GTM_CONTAINER_ID", "")
    current_year = data.get("CURRENT_YEAR", str(datetime.now().year))

    # Build service links for footer
    service_count = get_service_count(data)
    service_links_html = ""
    for n in range(1, service_count + 1):
        name = data.get(f"SERVICE_{n}_NAME", "")
        slug = data.get(f"SERVICE_{n}_SLUG", "")
        if name and slug:
            service_links_html += f'<li><a href="{main_domain}/services/{slug}.html" class="wss-footer__nav-link">{name}</a></li>'

    # Welcome post metadata
    today = date.today()
    post_date_iso = today.isoformat()
    post_date_display = today.strftime("%B %d, %Y")
    post_slug = f"{today.strftime('%Y-%m-%d')}-welcome-to-{_slugify(business_name)}-blog"

    # GTM snippets
    gtm_head = ""
    gtm_body = ""
    if gtm_id:
        gtm_head = f"""<!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
  new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  }})(window,document,'script','dataLayer','{gtm_id}');</script>"""
        gtm_body = f"""<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm_id}" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>"""

    # Build index.html
    index_html = _build_blog_index(
        business_name=business_name,
        primary_city=primary_city,
        state_code=state_code,
        phone_display=phone_display,
        phone_ttc=phone_ttc,
        tagline=tagline,
        logo=logo,
        pay_bill_url=pay_bill_url,
        main_domain=main_domain,
        blog_domain=blog_domain,
        facebook_url=facebook_url,
        gb_map=gb_map,
        email=email,
        street=street,
        zip_code=zip_code,
        service_links_html=service_links_html,
        current_year=current_year,
        gtm_head=gtm_head,
        gtm_body=gtm_body,
        post_slug=post_slug,
        post_date_display=post_date_display,
    )
    _write(output_path / "index.html", index_html)
    stats["pages"] += 1

    # 4. Generate welcome blog post
    welcome_post = _build_welcome_post(
        business_name=business_name,
        primary_city=primary_city,
        state_code=state_code,
        phone_display=phone_display,
        phone_ttc=phone_ttc,
        tagline=tagline,
        logo=logo,
        pay_bill_url=pay_bill_url,
        main_domain=main_domain,
        blog_domain=blog_domain,
        email=email,
        street=street,
        zip_code=zip_code,
        gb_map=gb_map,
        service_count=service_count,
        data=data,
        current_year=current_year,
        gtm_head=gtm_head,
        gtm_body=gtm_body,
        post_slug=post_slug,
        post_date_iso=post_date_iso,
        post_date_display=post_date_display,
    )
    _write(output_path / "posts" / f"{post_slug}.html", welcome_post)
    stats["posts"] += 1

    # 5. Copy _post-template.html (templatized)
    post_template = _build_post_template(
        business_name=business_name,
        logo=logo,
        pay_bill_url=pay_bill_url,
        phone_display=phone_display,
        phone_ttc=phone_ttc,
        main_domain=main_domain,
        blog_domain=blog_domain,
        primary_city=primary_city,
        state_code=state_code,
        email=email,
        street=street,
        zip_code=zip_code,
        gb_map=gb_map,
        current_year=current_year,
        gtm_head=gtm_head,
        gtm_body=gtm_body,
    )
    _write(output_path / "posts" / "_post-template.html", post_template)

    # 6. Generate RSS feed
    rss_content = _build_rss(
        business_name=business_name,
        blog_domain=blog_domain,
        post_slug=post_slug,
        post_date_iso=post_date_iso,
        primary_city=primary_city,
        state_code=state_code,
    )
    _write(output_path / "rss.xml", rss_content)

    # 7. Generate sitemap.xml
    posts = [{"slug": post_slug, "date": post_date_iso}]
    sitemap_content = build_blog_sitemap(blog_domain, posts)
    _write(output_path / "sitemap.xml", sitemap_content)

    # 8. Generate robots.txt
    robots = f"""# {business_name} Blog - robots.txt
# {blog_domain}

User-agent: *
Allow: /

# Sitemap
Sitemap: {blog_domain}/sitemap.xml

# Disallow template files
Disallow: /posts/_post-template.html
"""
    _write(output_path / "robots.txt", robots)

    # 9. Generate netlify.toml
    netlify = """# Blog - Netlify Configuration
# Static HTML site - no build required

[build]
  publish = "."
  command = ""

# Security headers
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "SAMEORIGIN"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Permissions-Policy = "geolocation=(), microphone=(), camera=()"

# Cache static assets
[[headers]]
  for = "/css/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/js/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

# Cache HTML pages for 1 hour
[[headers]]
  for = "/*.html"
  [headers.values]
    Cache-Control = "public, max-age=3600"
"""
    _write(output_path / "netlify.toml", netlify)

    # 10. Generate _redirects
    _write(output_path / "_redirects", "# Blog redirects\n")

    print(f"  Blog: {stats['pages']} pages, {stats['posts']} posts generated")
    return stats


def _write(path: Path, content: str):
    """Write content to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _slugify(text: str) -> str:
    """Convert text to URL slug."""
    import re
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def _build_blog_index(*, business_name, primary_city, state_code, phone_display,
                       phone_ttc, tagline, logo, pay_bill_url, main_domain,
                       blog_domain, facebook_url, gb_map, email, street,
                       zip_code, service_links_html, current_year,
                       gtm_head, gtm_body, post_slug, post_date_display):
    """Build the blog index.html page."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  {gtm_head}

  <!-- SEO Meta Tags -->
  <title>Blog | {business_name} | Storage Tips & News</title>
  <meta name="description" content="Read the latest storage tips, moving guides, and news from {business_name} in {primary_city}, {state_code}.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{blog_domain}/">

  <!-- Open Graph -->
  <meta property="og:title" content="Blog | {business_name}">
  <meta property="og:description" content="Storage tips, moving guides, and news from {business_name}.">
  <meta property="og:image" content="{logo}">
  <meta property="og:url" content="{blog_domain}/">
  <meta property="og:type" content="website">

  <!-- RSS Feed -->
  <link rel="alternate" type="application/rss+xml" title="{business_name} Blog" href="/rss.xml">

  <!-- Favicon -->
  <link rel="icon" type="image/png" href="{logo}">

  <!-- Stylesheet -->
  <link rel="stylesheet" href="/css/styles.css">
</head>
<body>
{gtm_body}

<!-- HEADER -->
<header class="wss-header">
  <nav class="wss-container">
    <div class="wss-header__inner">
      <a href="{main_domain}/"><img src="{logo}" alt="{business_name} Logo" class="wss-header__logo"></a>
      <div class="wss-header__nav">
        <a href="{main_domain}/" class="wss-header__nav-link">Home</a>
        <a href="/" class="wss-header__nav-link wss-header__nav-link--active">Blog</a>
        <a href="{main_domain}/size-guide.html" class="wss-header__nav-link">Size Guide</a>
        <a href="{main_domain}/faqs.html" class="wss-header__nav-link">FAQs</a>
      </div>
      <div class="wss-header__actions">
        <a href="tel:{phone_ttc}" class="wss-header__phone">
          <svg class="wss-header__phone-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
          <span class="wss-header__phone-text">{phone_display}</span>
        </a>
        <a href="{pay_bill_url}" target="_blank" rel="noopener noreferrer" class="wss-btn wss-btn--primary wss-btn--sm">Pay My Bill</a>
        <button type="button" class="wss-header__menu-toggle" aria-label="Open menu" data-menu-toggle>
          <svg class="wss-header__menu-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
      </div>
    </div>
    <div class="wss-header__mobile-menu" id="mobile-menu">
      <div class="wss-header__mobile-nav">
        <a href="{main_domain}/" class="wss-header__mobile-link">Home</a>
        <a href="/" class="wss-header__mobile-link wss-header__mobile-link--active">Blog</a>
        <a href="{main_domain}/size-guide.html" class="wss-header__mobile-link">Size Guide</a>
        <a href="{main_domain}/faqs.html" class="wss-header__mobile-link">FAQs</a>
      </div>
    </div>
  </nav>
</header>

<main>
  <!-- PAGE HERO -->
  <section class="wss-page-hero">
    <div class="wss-container">
      <h1 class="wss-page-hero__title">{business_name} Blog</h1>
      <p class="wss-page-hero__subtitle">Storage tips, moving guides, and news from our facility in {primary_city}, {state_code}</p>
    </div>
  </section>

  <!-- BLOG LISTING -->
  <section class="wss-section wss-section--white">
    <div class="wss-container">
      <div class="wss-grid wss-grid--3" style="gap: 2rem;">

        <!-- POST 1 (Welcome Post) -->
        <a href="/posts/{post_slug}.html" class="wss-blog-card" style="display: block; text-decoration: none; color: inherit; background: white; border-radius: 1rem; overflow: hidden; box-shadow: var(--wss-shadow-md); transition: box-shadow 0.3s, transform 0.3s;">
          <div style="padding: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
              <span style="font-size: 0.75rem; color: var(--wss-gray-500);">{post_date_display}</span>
              <span style="font-size: 0.625rem; background: var(--wss-primary-50); color: var(--wss-primary); padding: 0.25rem 0.5rem; border-radius: 9999px; font-weight: 500;">News</span>
            </div>
            <h2 style="font-size: var(--wss-text-xl); font-weight: 600; margin-bottom: 0.75rem; line-height: 1.3;">Welcome to the {business_name} Blog</h2>
            <p style="color: var(--wss-gray-600); font-size: var(--wss-text-sm); line-height: 1.6; margin-bottom: 1rem;">Your go-to resource for storage tips, moving guides, and facility news from {business_name} in {primary_city}, {state_code}.</p>
            <span style="color: var(--wss-primary); font-weight: 500; font-size: var(--wss-text-sm);">Read More &rarr;</span>
          </div>
        </a>

        <!-- ADD MORE POST CARDS HERE -->

      </div>
    </div>
  </section>

  <!-- CTA SECTION -->
  <section class="wss-section wss-cta">
    <div class="wss-container">
      <h2 class="wss-cta__title">Need Storage in {primary_city}?</h2>
      <p class="wss-cta__description">Browse our available units and reserve online today!</p>
      <div class="wss-cta__buttons">
        <a href="{main_domain}/#choose-unit" class="wss-btn wss-btn--white">View Available Units</a>
        <a href="tel:{phone_ttc}" class="wss-btn wss-btn--outline-white">Call {phone_display}</a>
      </div>
    </div>
  </section>
</main>

<!-- FOOTER -->
<footer class="wss-footer">
  <div class="wss-container wss-footer__main">
    <div class="wss-footer__grid">
      <div class="wss-footer__column">
        <img src="{logo}" alt="{business_name} Logo" class="wss-footer__logo">
        <p class="wss-footer__tagline">{tagline}</p>
        <div class="wss-footer__social">
          <a href="{facebook_url}" target="_blank" class="wss-footer__social-link" aria-label="Facebook"><svg class="wss-footer__social-icon" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg></a>
          <a href="{gb_map}" target="_blank" class="wss-footer__social-link" aria-label="Google Maps"><svg class="wss-footer__social-icon" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C7.802 0 4 3.403 4 7.602 4 11.8 7.469 16.812 12 24c4.531-7.188 8-12.2 8-16.398C20 3.403 16.199 0 12 0zm0 11a3 3 0 110-6 3 3 0 010 6z"/></svg></a>
        </div>
      </div>
      <div class="wss-footer__column"><h3 class="wss-footer__heading">Quick Links</h3><ul class="wss-footer__nav"><li><a href="{main_domain}/" class="wss-footer__nav-link">Home</a></li><li><a href="/" class="wss-footer__nav-link">Blog</a></li><li><a href="{main_domain}/size-guide.html" class="wss-footer__nav-link">Size Guide</a></li><li><a href="{main_domain}/about.html" class="wss-footer__nav-link">About Us</a></li><li><a href="{main_domain}/contact.html" class="wss-footer__nav-link">Contact</a></li></ul></div>
      <div class="wss-footer__column"><h3 class="wss-footer__heading">Our Services</h3><ul class="wss-footer__nav">{service_links_html}</ul></div>
      <div class="wss-footer__column"><h3 class="wss-footer__heading">Contact Us</h3><ul class="wss-footer__contact"><li class="wss-footer__contact-item"><svg class="wss-footer__contact-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg><a href="{gb_map}" target="_blank" class="wss-footer__contact-link">{street} {primary_city}, {state_code} {zip_code}</a></li><li class="wss-footer__contact-item"><svg class="wss-footer__contact-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg><a href="tel:{phone_ttc}" class="wss-footer__contact-link">{phone_display}</a></li><li class="wss-footer__contact-item"><svg class="wss-footer__contact-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg><a href="mailto:{email}" class="wss-footer__contact-link">{email}</a></li></ul></div>
    </div>
  </div>
  <div class="wss-footer__bottom"><div class="wss-container wss-footer__bottom-inner"><p>&copy; {current_year} {business_name}. All rights reserved.</p><div class="wss-footer__legal"><a href="{main_domain}/privacy.html" class="wss-footer__legal-link">Privacy Policy</a><a href="{main_domain}/terms.html" class="wss-footer__legal-link">Terms of Service</a></div></div></div>
</footer>

<script src="/js/main.js"></script>
</body>
</html>
"""


def _build_welcome_post(*, business_name, primary_city, state_code, phone_display,
                         phone_ttc, tagline, logo, pay_bill_url, main_domain,
                         blog_domain, email, street, zip_code, gb_map,
                         service_count, data, current_year,
                         gtm_head, gtm_body, post_slug, post_date_iso,
                         post_date_display):
    """Build the welcome blog post."""
    # Build services list
    services_html = ""
    for n in range(1, service_count + 1):
        name = data.get(f"SERVICE_{n}_NAME", "")
        slug = data.get(f"SERVICE_{n}_SLUG", "")
        desc = data.get(f"SERVICE_{n}_SHORT_DESC", "")
        if name:
            services_html += f"""
            <li><strong><a href="{main_domain}/services/{slug}.html" style="color: var(--wss-primary); text-decoration: none;">{name}</a></strong> - {desc}</li>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  {gtm_head}

  <!-- SEO Meta Tags -->
  <title>Welcome to the {business_name} Blog | {business_name}</title>
  <meta name="description" content="Welcome to the {business_name} blog. Your resource for storage tips, moving guides, and facility news in {primary_city}, {state_code}.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{blog_domain}/posts/{post_slug}.html">

  <!-- Open Graph -->
  <meta property="og:title" content="Welcome to the {business_name} Blog">
  <meta property="og:description" content="Your resource for storage tips, moving guides, and facility news.">
  <meta property="og:image" content="{logo}">
  <meta property="og:url" content="{blog_domain}/posts/{post_slug}.html">
  <meta property="og:type" content="article">
  <meta property="article:published_time" content="{post_date_iso}">

  <!-- RSS Feed -->
  <link rel="alternate" type="application/rss+xml" title="{business_name} Blog" href="/rss.xml">

  <!-- Favicon -->
  <link rel="icon" type="image/png" href="{logo}">

  <!-- Stylesheet -->
  <link rel="stylesheet" href="/css/styles.css">

  <!-- Article Schema -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "Welcome to the {business_name} Blog",
    "description": "Your resource for storage tips, moving guides, and facility news in {primary_city}, {state_code}.",
    "datePublished": "{post_date_iso}",
    "author": {{
      "@type": "Organization",
      "name": "{business_name}"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "{business_name}",
      "logo": {{
        "@type": "ImageObject",
        "url": "{logo}"
      }}
    }},
    "mainEntityOfPage": {{
      "@type": "WebPage",
      "@id": "{blog_domain}/posts/{post_slug}.html"
    }}
  }}
  </script>
</head>
<body>
{gtm_body}

<!-- HEADER -->
<header class="wss-header">
  <nav class="wss-container">
    <div class="wss-header__inner">
      <a href="{main_domain}/"><img src="{logo}" alt="{business_name} Logo" class="wss-header__logo"></a>
      <div class="wss-header__nav">
        <a href="{main_domain}/" class="wss-header__nav-link">Home</a>
        <a href="/" class="wss-header__nav-link wss-header__nav-link--active">Blog</a>
        <a href="{main_domain}/size-guide.html" class="wss-header__nav-link">Size Guide</a>
        <a href="{main_domain}/faqs.html" class="wss-header__nav-link">FAQs</a>
      </div>
      <div class="wss-header__actions">
        <a href="tel:{phone_ttc}" class="wss-header__phone">
          <svg class="wss-header__phone-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
          <span class="wss-header__phone-text">{phone_display}</span>
        </a>
        <a href="{pay_bill_url}" target="_blank" rel="noopener noreferrer" class="wss-btn wss-btn--primary wss-btn--sm">Pay My Bill</a>
        <button type="button" class="wss-header__menu-toggle" aria-label="Open menu" data-menu-toggle>
          <svg class="wss-header__menu-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
      </div>
    </div>
    <div class="wss-header__mobile-menu" id="mobile-menu">
      <div class="wss-header__mobile-nav">
        <a href="{main_domain}/" class="wss-header__mobile-link">Home</a>
        <a href="/" class="wss-header__mobile-link wss-header__mobile-link--active">Blog</a>
        <a href="{main_domain}/size-guide.html" class="wss-header__mobile-link">Size Guide</a>
        <a href="{main_domain}/faqs.html" class="wss-header__mobile-link">FAQs</a>
      </div>
    </div>
  </nav>
</header>

<main>
  <!-- BLOG POST -->
  <article class="wss-section wss-section--white">
    <div class="wss-container" style="max-width: 48rem;">

      <!-- Breadcrumb -->
      <nav style="margin-bottom: 2rem; font-size: var(--wss-text-sm); color: var(--wss-gray-500);">
        <a href="/" style="color: var(--wss-primary); text-decoration: none;">Blog</a>
        <span style="margin: 0 0.5rem;">/</span>
        <span>Welcome to the {business_name} Blog</span>
      </nav>

      <!-- Post Header -->
      <header style="margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
          <time datetime="{post_date_iso}" style="font-size: var(--wss-text-sm); color: var(--wss-gray-500);">{post_date_display}</time>
          <span style="font-size: 0.625rem; background: var(--wss-primary-50); color: var(--wss-primary); padding: 0.25rem 0.5rem; border-radius: 9999px; font-weight: 500;">News</span>
        </div>
        <h1 style="font-size: clamp(1.75rem, 4vw, 2.5rem); font-weight: 700; line-height: 1.2; margin-bottom: 1rem;">Welcome to the {business_name} Blog</h1>
        <p style="font-size: var(--wss-text-lg); color: var(--wss-gray-600); line-height: 1.6;">Your go-to resource for storage tips, moving guides, and facility news from {business_name} in {primary_city}, {state_code}.</p>
      </header>

      <!-- Post Content -->
      <div class="wss-legal-content">
        <p>Welcome to the official {business_name} blog! We're excited to share helpful resources, storage tips, and news from our facility located in {primary_city}, {state_code}.</p>

        <h2>What to Expect From Our Blog</h2>
        <p>Our blog will be your go-to resource for:</p>
        <ul>
          <li><strong>Storage Tips</strong> - Practical advice on packing, organizing, and making the most of your storage unit</li>
          <li><strong>Moving Guides</strong> - Step-by-step guides to make your move smoother</li>
          <li><strong>Size Guides</strong> - Help choosing the right unit size for your needs</li>
          <li><strong>Facility News</strong> - Updates about our facility and community</li>
        </ul>

        <h2>Our Storage Services</h2>
        <p>At {business_name}, we offer a variety of storage solutions to meet your needs:</p>
        <ul>{services_html}
        </ul>

        <h2>Get Started Today</h2>
        <p>Whether you're looking for personal storage, business storage, or vehicle storage, we're here to help. <a href="{main_domain}/#choose-unit" style="color: var(--wss-primary);">Browse our available units</a> or call us at <a href="tel:{phone_ttc}" style="color: var(--wss-primary);">{phone_display}</a> to get started.</p>

        <p>Stay tuned for more helpful content, and don't hesitate to <a href="{main_domain}/contact.html" style="color: var(--wss-primary);">reach out</a> if you have any questions!</p>
      </div>

      <!-- Post Footer -->
      <div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--wss-gray-200);">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem;">
          <a href="/" style="color: var(--wss-primary); text-decoration: none; font-weight: 500;">&larr; Back to Blog</a>
          <a href="{main_domain}/#choose-unit" class="wss-btn wss-btn--primary wss-btn--sm">Reserve a Unit</a>
        </div>
      </div>

    </div>
  </article>

  <!-- CTA SECTION -->
  <section class="wss-section wss-cta">
    <div class="wss-container">
      <h2 class="wss-cta__title">Need Storage in {primary_city}?</h2>
      <p class="wss-cta__description">Browse our available units and reserve online today!</p>
      <div class="wss-cta__buttons">
        <a href="{main_domain}/#choose-unit" class="wss-btn wss-btn--white">View Available Units</a>
        <a href="tel:{phone_ttc}" class="wss-btn wss-btn--outline-white">Call {phone_display}</a>
      </div>
    </div>
  </section>
</main>

<!-- FOOTER -->
<footer class="wss-footer">
  <div class="wss-container wss-footer__main">
    <div class="wss-footer__grid">
      <div class="wss-footer__column">
        <img src="{logo}" alt="{business_name} Logo" class="wss-footer__logo">
        <p class="wss-footer__tagline">{tagline}</p>
      </div>
      <div class="wss-footer__column"><h3 class="wss-footer__heading">Quick Links</h3><ul class="wss-footer__nav"><li><a href="{main_domain}/" class="wss-footer__nav-link">Home</a></li><li><a href="/" class="wss-footer__nav-link">Blog</a></li><li><a href="{main_domain}/size-guide.html" class="wss-footer__nav-link">Size Guide</a></li><li><a href="{main_domain}/about.html" class="wss-footer__nav-link">About Us</a></li><li><a href="{main_domain}/contact.html" class="wss-footer__nav-link">Contact</a></li></ul></div>
      <div class="wss-footer__column"><h3 class="wss-footer__heading">Contact Us</h3><ul class="wss-footer__contact"><li class="wss-footer__contact-item"><svg class="wss-footer__contact-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg><a href="{gb_map}" target="_blank" class="wss-footer__contact-link">{street} {primary_city}, {state_code} {zip_code}</a></li><li class="wss-footer__contact-item"><svg class="wss-footer__contact-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg><a href="tel:{phone_ttc}" class="wss-footer__contact-link">{phone_display}</a></li><li class="wss-footer__contact-item"><svg class="wss-footer__contact-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg><a href="mailto:{email}" class="wss-footer__contact-link">{email}</a></li></ul></div>
    </div>
  </div>
  <div class="wss-footer__bottom"><div class="wss-container wss-footer__bottom-inner"><p>&copy; {current_year} {business_name}. All rights reserved.</p><div class="wss-footer__legal"><a href="{main_domain}/privacy.html" class="wss-footer__legal-link">Privacy Policy</a><a href="{main_domain}/terms.html" class="wss-footer__legal-link">Terms of Service</a></div></div></div>
</footer>

<script src="/js/main.js"></script>
</body>
</html>
"""


def _build_post_template(*, business_name, logo, pay_bill_url, phone_display,
                          phone_ttc, main_domain, blog_domain, primary_city,
                          state_code, email, street, zip_code, gb_map,
                          current_year, gtm_head, gtm_body):
    """Build the reusable _post-template.html."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  {gtm_head}

  <!-- SEO Meta Tags -->
  <!-- REPLACE: POST_TITLE, POST_DATE, POST_DESCRIPTION, POST_SLUG -->
  <title>POST_TITLE | {business_name} Blog</title>
  <meta name="description" content="POST_DESCRIPTION">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{blog_domain}/posts/POST_SLUG.html">

  <!-- Open Graph -->
  <meta property="og:title" content="POST_TITLE | {business_name} Blog">
  <meta property="og:description" content="POST_DESCRIPTION">
  <meta property="og:image" content="{logo}">
  <meta property="og:url" content="{blog_domain}/posts/POST_SLUG.html">
  <meta property="og:type" content="article">
  <meta property="article:published_time" content="POST_DATE_ISO">

  <!-- RSS Feed -->
  <link rel="alternate" type="application/rss+xml" title="{business_name} Blog" href="/rss.xml">

  <!-- Favicon -->
  <link rel="icon" type="image/png" href="{logo}">

  <!-- Stylesheet -->
  <link rel="stylesheet" href="/css/styles.css">

  <!-- Article Schema -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "POST_TITLE",
    "description": "POST_DESCRIPTION",
    "datePublished": "POST_DATE_ISO",
    "author": {{
      "@type": "Organization",
      "name": "{business_name}"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "{business_name}",
      "logo": {{
        "@type": "ImageObject",
        "url": "{logo}"
      }}
    }},
    "mainEntityOfPage": {{
      "@type": "WebPage",
      "@id": "{blog_domain}/posts/POST_SLUG.html"
    }}
  }}
  </script>
</head>
<body>
{gtm_body}

<!-- HEADER -->
<header class="wss-header">
  <nav class="wss-container">
    <div class="wss-header__inner">
      <a href="{main_domain}/"><img src="{logo}" alt="{business_name} Logo" class="wss-header__logo"></a>
      <div class="wss-header__nav">
        <a href="{main_domain}/" class="wss-header__nav-link">Home</a>
        <a href="/" class="wss-header__nav-link wss-header__nav-link--active">Blog</a>
        <a href="{main_domain}/size-guide.html" class="wss-header__nav-link">Size Guide</a>
        <a href="{main_domain}/faqs.html" class="wss-header__nav-link">FAQs</a>
      </div>
      <div class="wss-header__actions">
        <a href="tel:{phone_ttc}" class="wss-header__phone">
          <svg class="wss-header__phone-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
          <span class="wss-header__phone-text">{phone_display}</span>
        </a>
        <a href="{pay_bill_url}" target="_blank" rel="noopener noreferrer" class="wss-btn wss-btn--primary wss-btn--sm">Pay My Bill</a>
        <button type="button" class="wss-header__menu-toggle" aria-label="Open menu" data-menu-toggle>
          <svg class="wss-header__menu-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
      </div>
    </div>
    <div class="wss-header__mobile-menu" id="mobile-menu">
      <div class="wss-header__mobile-nav">
        <a href="{main_domain}/" class="wss-header__mobile-link">Home</a>
        <a href="/" class="wss-header__mobile-link wss-header__mobile-link--active">Blog</a>
        <a href="{main_domain}/size-guide.html" class="wss-header__mobile-link">Size Guide</a>
        <a href="{main_domain}/faqs.html" class="wss-header__mobile-link">FAQs</a>
      </div>
    </div>
  </nav>
</header>

<main>
  <!-- BLOG POST -->
  <article class="wss-section wss-section--white">
    <div class="wss-container" style="max-width: 48rem;">

      <!-- Breadcrumb -->
      <nav style="margin-bottom: 2rem; font-size: var(--wss-text-sm); color: var(--wss-gray-500);">
        <a href="/" style="color: var(--wss-primary); text-decoration: none;">Blog</a>
        <span style="margin: 0 0.5rem;">/</span>
        <span>POST_TITLE</span>
      </nav>

      <!-- Post Header -->
      <header style="margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
          <time datetime="POST_DATE_ISO" style="font-size: var(--wss-text-sm); color: var(--wss-gray-500);">POST_DATE_DISPLAY</time>
          <span style="font-size: 0.625rem; background: var(--wss-primary-50); color: var(--wss-primary); padding: 0.25rem 0.5rem; border-radius: 9999px; font-weight: 500;">POST_TAG</span>
        </div>
        <h1 style="font-size: clamp(1.75rem, 4vw, 2.5rem); font-weight: 700; line-height: 1.2; margin-bottom: 1rem;">POST_TITLE</h1>
        <p style="font-size: var(--wss-text-lg); color: var(--wss-gray-600); line-height: 1.6;">POST_DESCRIPTION</p>
      </header>

      <!-- Post Content -->
      <div class="wss-legal-content">
        <!-- WRITE YOUR BLOG POST CONTENT HERE -->
        <h2>First Section Heading</h2>
        <p>Your content here...</p>
      </div>

      <!-- Post Footer -->
      <div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--wss-gray-200);">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem;">
          <a href="/" style="color: var(--wss-primary); text-decoration: none; font-weight: 500;">&larr; Back to Blog</a>
          <a href="{main_domain}/#choose-unit" class="wss-btn wss-btn--primary wss-btn--sm">Reserve a Unit</a>
        </div>
      </div>

    </div>
  </article>

  <!-- CTA SECTION -->
  <section class="wss-section wss-cta">
    <div class="wss-container">
      <h2 class="wss-cta__title">Need Storage in {primary_city}?</h2>
      <p class="wss-cta__description">Browse our available units and reserve online today!</p>
      <div class="wss-cta__buttons">
        <a href="{main_domain}/#choose-unit" class="wss-btn wss-btn--white">View Available Units</a>
        <a href="tel:{phone_ttc}" class="wss-btn wss-btn--outline-white">Call {phone_display}</a>
      </div>
    </div>
  </section>
</main>

<!-- FOOTER -->
<footer class="wss-footer">
  <div class="wss-container wss-footer__main">
    <div class="wss-footer__grid">
      <div class="wss-footer__column">
        <img src="{logo}" alt="{business_name} Logo" class="wss-footer__logo">
        <p class="wss-footer__tagline">Secure, affordable self storage in {primary_city}, {state_code}.</p>
      </div>
      <div class="wss-footer__column"><h3 class="wss-footer__heading">Quick Links</h3><ul class="wss-footer__nav"><li><a href="{main_domain}/" class="wss-footer__nav-link">Home</a></li><li><a href="/" class="wss-footer__nav-link">Blog</a></li><li><a href="{main_domain}/size-guide.html" class="wss-footer__nav-link">Size Guide</a></li><li><a href="{main_domain}/about.html" class="wss-footer__nav-link">About Us</a></li><li><a href="{main_domain}/contact.html" class="wss-footer__nav-link">Contact</a></li></ul></div>
      <div class="wss-footer__column"><h3 class="wss-footer__heading">Contact Us</h3><ul class="wss-footer__contact"><li class="wss-footer__contact-item"><svg class="wss-footer__contact-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg><a href="{gb_map}" target="_blank" class="wss-footer__contact-link">{street} {primary_city}, {state_code} {zip_code}</a></li><li class="wss-footer__contact-item"><svg class="wss-footer__contact-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg><a href="tel:{phone_ttc}" class="wss-footer__contact-link">{phone_display}</a></li><li class="wss-footer__contact-item"><svg class="wss-footer__contact-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg><a href="mailto:{email}" class="wss-footer__contact-link">{email}</a></li></ul></div>
    </div>
  </div>
  <div class="wss-footer__bottom"><div class="wss-container wss-footer__bottom-inner"><p>&copy; {current_year} {business_name}. All rights reserved.</p><div class="wss-footer__legal"><a href="{main_domain}/privacy.html" class="wss-footer__legal-link">Privacy Policy</a><a href="{main_domain}/terms.html" class="wss-footer__legal-link">Terms of Service</a></div></div></div>
</footer>

<script src="/js/main.js"></script>
</body>
</html>

<!--
HOW TO USE THIS TEMPLATE:
=========================
1. Copy this file to posts/ directory
2. Rename to: YYYY-MM-DD-post-slug.html (e.g., 2026-03-15-spring-cleaning-tips.html)
3. Replace all POST_* placeholders:
   - POST_TITLE: "Your Blog Post Title"
   - POST_SLUG: "2026-03-15-spring-cleaning-tips" (filename without .html)
   - POST_DATE_ISO: "2026-03-15" (YYYY-MM-DD format)
   - POST_DATE_DISPLAY: "March 15, 2026"
   - POST_DESCRIPTION: "A brief 1-2 sentence summary of the post"
   - POST_TAG: "Storage Tips" (or: "Moving Guide", "News", "How-To")
4. Write your content in the <div class="wss-legal-content"> section
5. Add a card to index.html for the new post
6. Add an entry to rss.xml
7. Commit and push to GitHub
-->
"""


def _build_rss(*, business_name, blog_domain, post_slug, post_date_iso,
               primary_city, state_code):
    """Build RSS feed XML."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{business_name} Blog</title>
    <description>Storage tips, moving guides, and news from {business_name} in {primary_city}, {state_code}.</description>
    <link>{blog_domain}/</link>
    <atom:link href="{blog_domain}/rss.xml" rel="self" type="application/rss+xml"/>
    <language>en-us</language>
    <lastBuildDate>{post_date_iso}</lastBuildDate>

    <item>
      <title>Welcome to the {business_name} Blog</title>
      <description>Your go-to resource for storage tips, moving guides, and facility news from {business_name}.</description>
      <link>{blog_domain}/posts/{post_slug}.html</link>
      <guid>{blog_domain}/posts/{post_slug}.html</guid>
      <pubDate>{post_date_iso}</pubDate>
    </item>
  </channel>
</rss>
"""
