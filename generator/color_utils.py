"""Generate color shade variants from a hex color using HSL manipulation."""

import colorsys
from typing import Dict


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple (0-255)."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex string."""
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_to_hsl(hex_color: str) -> tuple:
    """Convert hex color to HSL tuple (h: 0-360, s: 0-100, l: 0-100)."""
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return (h * 360, s * 100, l * 100)


def hsl_to_hex(h: float, s: float, l: float) -> str:
    """Convert HSL (h: 0-360, s: 0-100, l: 0-100) to hex string."""
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return rgb_to_hex(
        max(0, min(255, round(r * 255))),
        max(0, min(255, round(g * 255))),
        max(0, min(255, round(b * 255))),
    )


# Lightness targets for shade levels (Tailwind-inspired)
SHADE_LIGHTNESS = {
    50: 95,
    100: 90,
    200: 80,
    300: 70,
    400: 60,
    # 500 = base color (keep original)
    600: 40,
    700: 33,
    800: 26,
    900: 20,
    950: 14,
}


def generate_shades(hex_color: str) -> Dict[str, str]:
    """Generate Tailwind-style shade variants from a base hex color.

    Returns dict with keys like '50', '100', ..., '950' mapping to hex colors.
    """
    h, s, l = hex_to_hsl(hex_color)
    shades = {}

    for shade, target_lightness in SHADE_LIGHTNESS.items():
        shades[str(shade)] = hsl_to_hex(h, s, target_lightness)

    return shades


def generate_accent_600(hex_color: str) -> str:
    """Generate a darker variant (600 shade) of the accent color."""
    h, s, l = hex_to_hsl(hex_color)
    return hsl_to_hex(h, s, max(l - 8, 15))


def generate_variables_css(primary: str, secondary: str, accent: str) -> str:
    """Generate the complete _variables.css content with computed color shades."""
    primary_shades = generate_shades(primary)
    accent_600 = generate_accent_600(accent)

    return f"""/* =============================================================================
   Self Storage Site - Design Tokens (Auto-generated)
   ============================================================================= */

:root {{
  /* Brand Colors - Primary */
  --wss-primary: {primary};
  --wss-primary-50: {primary_shades['50']};
  --wss-primary-100: {primary_shades['100']};
  --wss-primary-200: {primary_shades['200']};
  --wss-primary-300: {primary_shades['300']};
  --wss-primary-400: {primary_shades['400']};
  --wss-primary-500: {primary};
  --wss-primary-600: {primary_shades['600']};
  --wss-primary-700: {primary_shades['700']};
  --wss-primary-800: {primary_shades['800']};
  --wss-primary-900: {primary_shades['900']};
  --wss-primary-950: {primary_shades['950']};

  /* Secondary (White/Light) */
  --wss-secondary: {secondary};
  --wss-secondary-50: #FFFFFF;
  --wss-secondary-100: #FAFAFA;
  --wss-secondary-200: #F5F5F5;
  --wss-secondary-300: #E5E5E5;
  --wss-secondary-400: #D4D4D4;

  /* Accent */
  --wss-accent: {accent};
  --wss-accent-500: {accent};
  --wss-accent-600: {accent_600};

  /* Gray Scale (Standard) */
  --wss-gray-50: #f9fafb;
  --wss-gray-100: #f3f4f6;
  --wss-gray-200: #e5e7eb;
  --wss-gray-300: #d1d5db;
  --wss-gray-400: #9ca3af;
  --wss-gray-500: #6b7280;
  --wss-gray-600: #4b5563;
  --wss-gray-700: #374151;
  --wss-gray-800: #1f2937;
  --wss-gray-900: #111827;

  /* Semantic Colors */
  --wss-success: #22c55e;
  --wss-warning: #f59e0b;
  --wss-error: #ef4444;
  --wss-info: #3b82f6;

  --wss-text: var(--wss-gray-900);
  --wss-text-muted: var(--wss-gray-600);
  --wss-bg: #ffffff;
  --wss-bg-alt: var(--wss-gray-50);

  /* Typography */
  --wss-font-heading: 'Montserrat', system-ui, -apple-system, sans-serif;
  --wss-font-body: 'Inter', system-ui, -apple-system, sans-serif;

  --wss-text-xs: 0.75rem;
  --wss-text-sm: 0.875rem;
  --wss-text-base: 1rem;
  --wss-text-lg: 1.125rem;
  --wss-text-xl: 1.25rem;
  --wss-text-2xl: 1.5rem;
  --wss-text-3xl: 1.875rem;
  --wss-text-4xl: 2.25rem;
  --wss-text-5xl: 3rem;
  --wss-text-6xl: 3.75rem;

  /* Spacing Scale */
  --wss-space-1: 0.25rem;
  --wss-space-2: 0.5rem;
  --wss-space-3: 0.75rem;
  --wss-space-4: 1rem;
  --wss-space-5: 1.25rem;
  --wss-space-6: 1.5rem;
  --wss-space-8: 2rem;
  --wss-space-10: 2.5rem;
  --wss-space-12: 3rem;
  --wss-space-16: 4rem;
  --wss-space-20: 5rem;
  --wss-space-24: 6rem;

  /* Layout */
  --wss-max-width: 80rem;
  --wss-container-padding: 1rem;

  /* Border Radius */
  --wss-radius-sm: 0.25rem;
  --wss-radius: 0.375rem;
  --wss-radius-md: 0.5rem;
  --wss-radius-lg: 0.5rem;
  --wss-radius-xl: 0.75rem;
  --wss-radius-2xl: 1rem;
  --wss-radius-3xl: 1.5rem;
  --wss-radius-full: 9999px;

  /* Shadows */
  --wss-shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --wss-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --wss-shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --wss-shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --wss-shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --wss-shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);

  /* Transitions */
  --wss-transition: 150ms ease;
  --wss-transition-fast: 100ms ease;
  --wss-transition-slow: 300ms ease;
  --wss-transition-slower: 500ms ease;
}}
"""
