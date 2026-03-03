"""Generate sitemap.xml dynamically based on site pages."""

from datetime import date
from typing import Dict, List

from .excel_reader import get_service_count, get_city_count


def build_sitemap(data: Dict[str, str]) -> str:
    """Build sitemap.xml content for the main site."""
    domain = data.get("DOMAIN", "https://example.com/").rstrip("/")
    today = date.today().isoformat()
    service_count = get_service_count(data)
    city_count = get_city_count(data)

    urls = []

    # Homepage
    urls.append(_url(f"{domain}/", today, "weekly", "1.0"))

    # Core pages
    for page in ["about.html", "contact.html", "size-guide.html", "faqs.html"]:
        urls.append(_url(f"{domain}/{page}", today, "monthly", "0.8"))

    # Services index
    urls.append(_url(f"{domain}/services/", today, "monthly", "0.8"))

    # Individual service pages
    for n in range(1, service_count + 1):
        slug = data.get(f"SERVICE_{n}_SLUG", "")
        if slug:
            urls.append(_url(f"{domain}/services/{slug}.html", today, "monthly", "0.7"))

    # Cities index
    urls.append(_url(f"{domain}/cities/", today, "monthly", "0.8"))

    # Individual city pages
    for n in range(1, city_count + 1):
        slug = data.get(f"CITY_{n}_SLUG", "")
        if slug:
            urls.append(_url(f"{domain}/cities/{slug}.html", today, "monthly", "0.7"))

    # Legal pages (lower priority)
    urls.append(_url(f"{domain}/privacy.html", today, "yearly", "0.3"))
    urls.append(_url(f"{domain}/terms.html", today, "yearly", "0.3"))

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(urls)}
</urlset>
"""


def build_blog_sitemap(blog_domain: str, posts: List[Dict[str, str]] = None) -> str:
    """Build sitemap.xml content for the blog site."""
    blog_domain = blog_domain.rstrip("/")
    today = date.today().isoformat()

    urls = []
    urls.append(_url(f"{blog_domain}/", today, "weekly", "1.0"))

    if posts:
        for post in posts:
            slug = post.get("slug", "")
            post_date = post.get("date", today)
            if slug:
                urls.append(_url(
                    f"{blog_domain}/posts/{slug}.html",
                    post_date, "monthly", "0.8"
                ))

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(urls)}
</urlset>
"""


def _url(loc: str, lastmod: str, changefreq: str, priority: str) -> str:
    """Build a single <url> element."""
    return f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>
"""
