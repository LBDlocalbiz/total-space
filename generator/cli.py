"""CLI interface for the storage site generator."""

import os
import sys
from pathlib import Path

import click

from .excel_reader import read_excel, get_service_count, get_city_count, get_enabled_units
from .validators import validate_data
from .site_builder import build_main_site
from .blog_builder import build_blog
from .llm_index_builder import build_llm_index


def _get_template_dir():
    """Get the templates directory path (relative to this package)."""
    return str(Path(__file__).parent.parent / "templates")


@click.command()
@click.argument("excel_file", type=click.Path(exists=True))
@click.option("-o", "--output", "output_dir", default="./output",
              help="Output directory (default: ./output)")
@click.option("--validate-only", is_flag=True,
              help="Only validate the Excel file, don't generate")
@click.option("--main-only", is_flag=True,
              help="Generate only the main site, skip the blog")
@click.option("--blog-domain", default="",
              help="Blog domain (e.g. https://blog.example.com). Auto-derived if not set.")
@click.option("--project-name", default="",
              help="Project folder name. Auto-derived from business name if not set.")
def main(excel_file, output_dir, validate_only, main_only, blog_domain, project_name):
    """Generate a storage facility website from an Excel data file.

    EXCEL_FILE is the path to the Excel data file with site content.
    """
    click.echo("=" * 60)
    click.echo("  Storage Site Generator v1.0")
    click.echo("=" * 60)
    click.echo()

    # Step 1: Read Excel data
    click.echo(f"Reading Excel file: {excel_file}")
    try:
        data = read_excel(excel_file)
    except Exception as e:
        click.echo(f"ERROR: Failed to read Excel file: {e}", err=True)
        sys.exit(1)

    service_count = get_service_count(data)
    city_count = get_city_count(data)
    enabled_units = get_enabled_units(data)

    click.echo(f"  Found: {len(data)} data fields")
    click.echo(f"  Services: {service_count}")
    click.echo(f"  Cities: {city_count}")
    click.echo(f"  Enabled units: {len(enabled_units)}")
    click.echo()

    # Step 2: Validate
    click.echo("Validating data...")
    errors, warnings = validate_data(data)

    for w in warnings:
        click.echo(f"  WARNING: {w}")

    if errors:
        click.echo()
        for e in errors:
            click.echo(f"  ERROR: {e}", err=True)
        click.echo()
        click.echo(f"Validation failed with {len(errors)} error(s).", err=True)
        sys.exit(1)

    if warnings:
        click.echo(f"  {len(warnings)} warning(s)")

    click.echo("  Validation passed!")
    click.echo()

    if validate_only:
        click.echo("Validate-only mode. Exiting.")
        return

    # Step 3: Determine output paths
    if not project_name:
        # Derive from business name
        business_name = data.get("BUSINESS_NAME", "storage-site")
        project_name = business_name.lower().strip()
        project_name = "".join(c if c.isalnum() or c in " -_" else "" for c in project_name)
        project_name = project_name.replace(" ", "-").replace("_", "-")
        while "--" in project_name:
            project_name = project_name.replace("--", "-")
        project_name = project_name.strip("-")

    main_output = os.path.join(output_dir, project_name)
    blog_output = os.path.join(output_dir, f"{project_name}-blog")

    template_dir = _get_template_dir()
    main_template = os.path.join(template_dir, "main")
    blog_template = os.path.join(template_dir, "blog")

    # Determine blog domain
    main_domain = data.get("DOMAIN", "https://example.com/").rstrip("/")
    if not blog_domain:
        domain_bare = main_domain.replace("https://", "").replace("http://", "")
        blog_domain = f"https://blog.{domain_bare}"

    # Step 4: Build main site
    click.echo(f"Building main site -> {main_output}")
    try:
        main_stats = build_main_site(data, main_template, main_output, blog_domain)
    except Exception as e:
        click.echo(f"ERROR building main site: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    click.echo()

    # Step 5: Build LLM index
    click.echo("Generating llm-index.json...")
    try:
        llm_content = build_llm_index(data, blog_domain)
        llm_path = os.path.join(main_output, "llm-index.json")
        with open(llm_path, "w", encoding="utf-8") as f:
            f.write(llm_content)
        click.echo("  llm-index.json generated")
    except Exception as e:
        click.echo(f"  WARNING: Failed to generate llm-index.json: {e}")
    click.echo()

    # Step 6: Build blog (unless --main-only)
    if not main_only:
        click.echo(f"Building blog -> {blog_output}")
        try:
            blog_stats = build_blog(
                data, blog_template, blog_output,
                blog_domain=blog_domain,
                main_domain=main_domain,
            )
        except Exception as e:
            click.echo(f"ERROR building blog: {e}", err=True)
            import traceback
            traceback.print_exc()
            sys.exit(1)
        click.echo()

    # Step 7: Summary
    click.echo("=" * 60)
    click.echo("  Generation Complete!")
    click.echo("=" * 60)
    click.echo()
    click.echo(f"  Main site: {main_output}/")
    if not main_only:
        click.echo(f"  Blog:      {blog_output}/")
    click.echo()
    click.echo(f"  Business:  {data.get('BUSINESS_NAME', 'N/A')}")
    click.echo(f"  Domain:    {main_domain}")
    if not main_only:
        click.echo(f"  Blog:      {blog_domain}")
    click.echo(f"  Services:  {service_count}")
    click.echo(f"  Cities:    {city_count}")
    click.echo()
    click.echo("Next steps:")
    click.echo("  1. Review generated files")
    click.echo("  2. Create GitHub repo and push main site")
    click.echo("  3. Create GitHub repo and push blog")
    click.echo("  4. Deploy both to Netlify")
    click.echo("  5. Configure custom domains and DNS")
