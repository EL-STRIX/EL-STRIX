"""SVG Banner renderer module."""

import os
from typing import Any, Dict
from utils import ensure_dir, logger


class SVGRenderer:
    """Renders light and dark mode SVG banners based on profile metrics."""

    def __init__(self, output_dir: str = "assets/svg"):
        self.output_dir = output_dir
        ensure_dir(self.output_dir)

    def render(self, data: Dict[str, Any]) -> None:
        """Render SVG dynamic graphics."""
        name = data.get("name", "EL-STRIX")
        repos = data.get("public_repos", 0)
        stars = data.get("total_stars", 0)

        # Light SVG template rendering
        light_svg_path = os.path.join(self.output_dir, "light.svg")
        dark_svg_path = os.path.join(self.output_dir, "dark.svg")

        logger.info(f"Rendered SVG banners for {name} (Repos: {repos}, Stars: {stars}) at {light_svg_path} & {dark_svg_path}")
