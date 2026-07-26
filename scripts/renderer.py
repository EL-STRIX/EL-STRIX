"""SVG Banner renderer module for EL-STRIX."""

import json
import os
from datetime import UTC, datetime

from config_loader import ConfigLoader
from logger import logger
from paths import PathManager
from utils import ensure_dir


class SVGRenderer:
    """Complete SVG Profile Rendering Engine (Phase 05)."""

    def __init__(self, output_dir: str | None = None):
        self.output_dir = output_dir or str(PathManager.ASSET_SVG_DIR)
        ensure_dir(self.output_dir)
        
        # New terminal dimensions
        self.width = 1800
        self.left_panel_width = 750
        self.right_panel_width = 1000
        self.min_height = 800
        
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

        self.font_family = "Consolas, 'Courier New', monospace"

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

    def _render_terminal_line(self, parts: list[tuple[str, str]], current_y: int, font_size: int = 18) -> str:
        """Render a single line of terminal text with multiple colors."""
        svg = f'<text x="0" y="{current_y}" xml:space="preserve" font-size="{font_size}" class="cli-text">'
        for text, color in parts:
            escaped_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            svg += f'<tspan fill="{color}">{escaped_text}</tspan>'
        svg += '</text>\\n'
        return svg

    def render(self) -> None:
        """Execute the dynamic layout engine and render SVGs."""
        logger.info("--- PHASE 05: SVG RENDERER STARTED ---")
        
        for mode in ["light", "dark"]:
            logger.info(f"Generating {mode} theme layout...")
            
            # Use fixed terminal colors matching the image aesthetics
            if mode == "dark":
                bg = "#0d1117"
                text_main = "#c9d1d9"
                text_dim = "#6e7681"
                text_key = "#d2a8ff"  # Purple-ish
                text_val = "#79c0ff"  # Blue-ish
                text_highlight = "#e3b341" # Orange/Gold
            else:
                bg = "#ffffff"
                text_main = "#24292f"
                text_dim = "#57606a"
                text_key = "#0550ae"
                text_val = "#0969da"
                text_highlight = "#b08800"

            ascii_content = self._get_ascii_svg_content(mode)
            
            right_panel_svg = ""
            current_y = 60
            line_height = 30
            
            MAX_LEN = 80
            
            def render_section_header(title: str):
                dash_count = MAX_LEN - len(title) - 1
                if dash_count < 0: dash_count = 0
                return self._render_terminal_line([
                    (f"{title} ", text_val),
                    ("-" * dash_count, text_dim)
                ], current_y)
                
            def render_dot_line(key: str, val: str):
                dots_count = MAX_LEN - len(key) - len(val) - 5
                if dots_count < 2: dots_count = 2
                dots = "." * dots_count
                return self._render_terminal_line([
                    (". ", text_dim),
                    (f"{key}: ", text_highlight),
                    (f"{dots} ", text_dim),
                    (val, text_main)
                ], current_y)
            
            # Header
            right_panel_svg += render_section_header("sujay@EL-STRIX")
            current_y += line_height
            
            # Tech Stack
            tech_stack = [
                ("OS", "Windows, Linux, Android"),
                ("Tooling", "VS Code, ZBrains IDE, Git"),
                ("Programming", "C, C++, Java, Go, Python, JavaScript, PHP"),
                ("Frontend", "HTML5, CSS3, Tailwind, Bootstrap, React, Vanilla JS"),
                ("Backend", "Node.js, Express"),
                ("Database", "MySQL"),
                ("Tools", "Git, GitHub Actions, Vercel"),
                ("Languages", "English, Bengali, Hindi")
            ]
            
            for key, val in tech_stack:
                right_panel_svg += render_dot_line(key, val)
                current_y += line_height
                
            current_y += line_height
            
            # Contact
            right_panel_svg += render_section_header("- Contact")
            current_y += line_height
            
            contacts = [
                ("Portfolio", "development phase"),
                ("LinkedIn", "https://www.linkedin.com/in/sujay-paul-684537374/"),
                ("GitHub", "https://github.com/EL-STRIX"),
                ("Email", "sujaypaul892@gmail.com"),
                ("Location", "Barasat, Kolkata, West Bengal, India")
            ]
            
            for key, val in contacts:
                right_panel_svg += render_dot_line(key, val)
                current_y += line_height
                
            current_y += line_height
            
            # Featured Projects
            right_panel_svg += render_section_header("- Featured Projects")
            current_y += line_height
            
            projects = [
                ("dYZr C Games Collection", "Development"),
                ("dY? Finzo Banking System", "Development Phase")
            ]
            
            for proj, status in projects:
                right_panel_svg += render_dot_line(proj, status)
                current_y += line_height
                
            current_y += line_height
            
            # GitHub Stats
            right_panel_svg += render_section_header("- GitHub Stats")
            current_y += line_height
            
            stats_data = [
                ("Repos:", str(self.stats.get("repositories", {}).get("repository_count", 0)), 
                 "Stars:", str(self.stats.get("stars", {}).get("total_stars", 0))),
                 
                ("Commits:", str(self.stats.get("commits", {}).get("total_commits", 0)),
                 "Followers:", str(self.stats.get("profile", {}).get("total_followers", 0))),
                 
                ("Contributions:", str(self.stats.get("contributions", {}).get("total_contributions", 0)),
                 "Pull Requests:", str(self.stats.get("pull_requests", {}).get("total_pull_requests", 0))),
                 
                ("Issues:", str(self.stats.get("issues", {}).get("total_issues", 0)),
                 "Releases:", str(self.stats.get("releases", {}).get("total_releases", 0)))
            ]
            
            for k1, v1, k2, v2 in stats_data:
                # Format: . Repos: .... 95 | Stars: ............ 342
                col1_len = 36
                dots1_count = col1_len - len(k1) - len(v1) - 4
                if dots1_count < 2: dots1_count = 2
                dots1 = "." * dots1_count
                
                col2_len = 36
                dots2_count = col2_len - len(k2) - len(v2) - 3
                if dots2_count < 2: dots2_count = 2
                dots2 = "." * dots2_count
                
                right_panel_svg += self._render_terminal_line([
                    (". ", text_dim),
                    (k1 + " ", text_highlight),
                    (dots1 + " ", text_dim),
                    (v1 + " ", text_main),
                    ("| ", text_dim),
                    (k2 + " ", text_highlight),
                    (dots2 + " ", text_dim),
                    (v2, text_main)
                ], current_y)
                current_y += line_height
                
            current_y += line_height
            
            # Generate Footer
            now = datetime.now(UTC).strftime("%d %b %Y")
            right_panel_svg += self._render_terminal_line([
                ("Generated Automatically by GitHub Actions. Last Run: " + now, text_dim)
            ], current_y, font_size=14)
            
            final_height = current_y + 40
            
            # Master SVG Template
            svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {final_height}" width="{self.width}" height="{final_height}">
    <!-- Background -->
    <rect width="100%" height="100%" fill="{bg}" rx="12"/>
    

    
    <style>
        .cli-text {{
            font-family: monospace;
        }}
        .ascii-text {{ 
            font-family: monospace; 
            font-size: 12px; 
            fill: {text_main}; 
            white-space: pre; 
        }}
    </style>
    
    <!-- Left Panel (ASCII Avatar) -->
    <g transform="translate(40, 60) scale(1.4, 1.4)">
        <g class="ascii-text">
            {ascii_content}
        </g>
    </g>

    <!-- Right Panel (Profile and Statistics) -->
    <g transform="translate({self.left_panel_width + 120}, 0)">
        {right_panel_svg}
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
