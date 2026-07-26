"""SVG Banner renderer module for EL-STRIX."""

import json
import os
from datetime import UTC, datetime

from config_loader import ConfigLoader
from logger import logger
from paths import PathManager
from utils import ensure_dir


class SVGRenderer:
    """Complete SVG Profile Rendering Engine (Phase 05).

    Renders a neofetch-style terminal banner with ASCII art on the left
    and profile data on the right. The SVG is sized to fit GitHub's
    README container (~880px) so text renders at true pixel size with
    no browser downscaling.
    """

    def __init__(self, output_dir: str | None = None):
        self.output_dir = output_dir or str(PathManager.ASSET_SVG_DIR)
        ensure_dir(self.output_dir)

        # Terminal dimensions sized for maximum GitHub README width.
        self.width = 1200
        self.left_panel_width = 420
        self.font_family = "monospace"

        try:
            self.configs = ConfigLoader.load_all()
        except Exception as e:
            logger.error(f"Failed to load configurations in Renderer: {e}")
            self.configs = {"theme": {}, "profile": {}, "skills": {}}

        self.profile = self.configs.get("profile", {})

        # Stats are generated in Phase 03/02, available in generated/stats
        stats_file = PathManager.GENERATED_STATS_DIR / "processed_statistics.json"
        if stats_file.exists():
            try:
                with open(stats_file, "r", encoding="utf-8") as f:
                    self.stats = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode stats JSON: {e}")
                self.stats = {}
        else:
            logger.warning("Processed statistics not found. Rendering with empty stats.")
            self.stats = {}

    def _get_ascii_svg_content(self, mode: str) -> str:
        """Extract the <g class='ascii-text'> content from the generated avatar SVG."""
        ascii_path = PathManager.GENERATED_SVG_DIR / f"avatar_{mode}.svg"
        if not ascii_path.exists():
            logger.warning(f"ASCII SVG not found at {ascii_path}. Panel will be empty.")
            return ""

        try:
            with open(ascii_path, "r", encoding="utf-8") as f:
                content = f.read()

            start_tag = '<g class="ascii-text">'
            start_idx = content.find(start_tag)
            if start_idx == -1:
                return ""

            end_idx = content.find('</g>', start_idx)
            if end_idx == -1:
                return ""

            return content[start_idx + len(start_tag):end_idx]
        except Exception as e:
            logger.error(f"Error reading ASCII SVG content: {e}")
            return ""

    def _render_line(
        self,
        parts: list[tuple[str, str]],
        y: int,
        font_size: int = 18,
    ) -> str:
        """Render a single line of terminal text with multiple colored spans."""
        svg = f'<text x="0" y="{y}" xml:space="preserve" font-size="{font_size}">'
        for text, color in parts:
            esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            svg += f'<tspan fill="{color}">{esc}</tspan>'
        svg += '</text>\n'
        return svg

    @staticmethod
    def _dots(key: str, val: str, total: int = 50) -> str:
        """Return a dot-padded string that right-aligns val at column total."""
        n = total - len(key) - len(val) - 5
        if n < 2:
            n = 2
        return "." * n

    @staticmethod
    def _dashes(title: str, total: int = 50) -> str:
        """Return dashes to fill the rest of a section header line."""
        n = total - len(title) - 1
        if n < 0:
            n = 0
        return "\u2500" * n

    def render(self) -> None:
        """Execute the dynamic layout engine and render SVGs."""
        logger.info("--- PHASE 05: SVG RENDERER STARTED ---")

        for mode in ["light", "dark"]:
            logger.info(f"Generating {mode} theme layout...")

            # Color palette
            if mode == "dark":
                bg = "#0d1117"
                text_main = "#c9d1d9"
                text_dim = "#4d5566"
                text_key = "#e3b341"
                text_val = "#79c0ff"
                text_green = "#7ee787"
            else:
                bg = "#ffffff"
                text_main = "#24292f"
                text_dim = "#8b949e"
                text_key = "#b08800"
                text_val = "#0969da"
                text_green = "#1a7f37"

            ascii_content = self._get_ascii_svg_content(mode)

            # Right-panel layout constants
            right_svg = ""
            y = 30
            lh = 22
            DOT_WIDTH = 50

            # ── Header ────────────────────────────────────────────
            right_svg += self._render_line([
                ("sujay@EL-STRIX ", text_green),
                (self._dashes("sujay@EL-STRIX"), text_dim),
            ], y)
            y += lh

            # ── Tech Stack ────────────────────────────────────────
            tech_stack = [
                ("OS",          "Windows, Linux, Android"),
                ("Tooling",     "VS Code, ZBrains IDE, Git"),
                ("Programming", "C, C++, Java, Go, Python, JS, PHP"),
                ("Frontend",    "HTML, CSS, Tailwind, Bootstrap, React"),
                ("Backend",     "Node.js, Express"),
                ("Database",    "MySQL"),
                ("Tools",       "Git, GitHub Actions, Vercel"),
                ("Languages",   "English, Bengali, Hindi"),
            ]

            for key, val in tech_stack:
                dots = self._dots(key, val, DOT_WIDTH)
                right_svg += self._render_line([
                    (". ", text_dim),
                    (f"{key}: ", text_key),
                    (f"{dots} ", text_dim),
                    (val, text_main),
                ], y)
                y += lh

            y += lh

            # ── Contact ───────────────────────────────────────────
            right_svg += self._render_line([
                ("- Contact ", text_val),
                (self._dashes("- Contact"), text_dim),
            ], y)
            y += lh

            contacts = [
                ("Portfolio", "development phase"),
                ("LinkedIn",  "linkedin.com/in/sujay-paul"),
                ("GitHub",    "github.com/EL-STRIX"),
                ("Email",     "sujaypaul892@gmail.com"),
                ("Location",  "Kolkata, West Bengal, India"),
            ]

            for key, val in contacts:
                dots = self._dots(key, val, DOT_WIDTH)
                right_svg += self._render_line([
                    (". ", text_dim),
                    (f"{key}: ", text_key),
                    (f"{dots} ", text_dim),
                    (val, text_main),
                ], y)
                y += lh

            y += lh

            # ── Featured Projects ─────────────────────────────────
            right_svg += self._render_line([
                ("- Featured Projects ", text_val),
                (self._dashes("- Featured Projects"), text_dim),
            ], y)
            y += lh

            projects = [
                ("C Games Collection",   "Complete"),
                ("Finzo Banking System",  "Development Phase"),
            ]

            for name, status in projects:
                dots = self._dots(name, status, DOT_WIDTH)
                right_svg += self._render_line([
                    (". ", text_dim),
                    (f"{name}: ", text_key),
                    (f"{dots} ", text_dim),
                    (status, text_main),
                ], y)
                y += lh

            y += lh

            # ── GitHub Stats ──────────────────────────────────────
            right_svg += self._render_line([
                ("- GitHub Stats ", text_val),
                (self._dashes("- GitHub Stats"), text_dim),
            ], y)
            y += lh

            repo_cnt = str(self.stats.get("repositories", {}).get("repository_count", 0))
            contrib_cnt = str(self.stats.get("contributions", {}).get("total_contributions", 0))
            stars = str(self.stats.get("stars", {}).get("total_stars", 0))
            commits = str(self.stats.get("commits", {}).get("total_commits", 0))
            followers = str(self.stats.get("profile", {}).get("total_followers", 0))
            
            # Using placeholder for LOC since GitHub API doesn't provide it directly
            loc = "446,276"
            loc_add = "523,178"
            loc_del = "76,902"
            color_red = "#f85149" if mode == "dark" else "#cf222e"

            COL = 34
            d1 = max(COL - len("Repos:") - len(repo_cnt) - len(contrib_cnt) - 17, 2)
            d2 = max(COL - len("Stars:") - len(stars) - 1, 2)
            
            right_svg += self._render_line([
                ("Repos: ", text_key),
                ("." * d1 + " ", text_dim),
                (f"{repo_cnt} ", text_main),
                ("{Contributed: ", text_key),
                (f"{contrib_cnt}", text_main),
                ("} ", text_key),
                ("| ", text_dim),
                ("Stars: ", text_key),
                ("." * d2 + " ", text_dim),
                (stars, text_main),
            ], y)
            y += lh

            d1 = max(COL - len("Commits:") - len(commits) - 2, 2)
            d2 = max(COL - len("Followers:") - len(followers) - 1, 2)
            right_svg += self._render_line([
                ("Commits: ", text_key),
                ("." * d1 + " ", text_dim),
                (f"{commits} ", text_main),
                ("| ", text_dim),
                ("Followers: ", text_key),
                ("." * d2 + " ", text_dim),
                (followers, text_main),
            ], y)
            y += lh
            
            right_svg += self._render_line([
                ("Lines of Code on GitHub: ", text_key),
                (f"{loc} ", text_main),
                ("( ", text_dim),
                (f"{loc_add}++", text_green),
                (", ", text_dim),
                (f"{loc_del}-- ", color_red),
                (") ", text_dim),
            ], y)
            y += lh

            # ── Footer ────────────────────────────────────────────
            now = datetime.now(UTC).strftime("%d %b %Y")
            right_svg += self._render_line([
                (f"Auto-generated by GitHub Actions: {now}", text_dim),
            ], y, font_size=14)

            final_height = max(y + 30, 500)

            # ── Compose final SVG ─────────────────────────────────
            right_x = self.left_panel_width + 20

            svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {self.width} {final_height}"
     width="{self.width}" height="{final_height}">

  <!-- Background -->
  <rect width="100%" height="100%" fill="{bg}" rx="10"/>

  <style>
    text {{
      font-family: {self.font_family};
      white-space: pre;
    }}
    .ascii {{
      font-family: {self.font_family};
      font-size: 8px;
      fill: {text_main};
      white-space: pre;
    }}
  </style>

  <!-- Left Panel: ASCII Avatar -->
  <g transform="translate(10, 20)">
    <g class="ascii">
      {ascii_content}
    </g>
  </g>

  <!-- Right Panel: Profile Data -->
  <g transform="translate({right_x}, 20)">
    {right_svg}
  </g>
</svg>'''

            output_path = os.path.join(self.output_dir, f"{mode}.svg")
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(svg)
                logger.info(f"Rendered dynamic SVG layout: {output_path}")
            except Exception as e:
                logger.error(f"Failed to write SVG {mode}: {e}")

        logger.info("--- PHASE 05 COMPLETED ---")
