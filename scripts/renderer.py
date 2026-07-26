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
        
        self.width = 1200
        self.left_panel_width = 580
        self.right_panel_width = 560
        self.min_height = 800
        
        try:
            self.configs = ConfigLoader.load_all()
        except Exception as e:
            logger.error(f"Failed to load configurations in Renderer: {e}")
            self.configs = {"theme": {}, "profile": {}, "skills": {}}
            
        self.profile = self.configs.get("profile", {})
        self.skills = self.configs.get("skills", {})
        self.theme_config = self.configs.get("theme", {})
        
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

        self.font_family = "Segoe UI, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'"

    def _get_theme_colors(self, mode: str) -> dict[str, str]:
        """Fetch theme colors from config or use intelligent defaults."""
        if mode in self.theme_config:
            return self.theme_config[mode]
        # Fallback to robust defaults
        if mode == "dark":
            return {"background": "#0d1117", "text": "#c9d1d9", "primary": "#58a6ff", "secondary": "#8b949e"}
        return {"background": "#ffffff", "text": "#24292f", "primary": "#0969da", "secondary": "#57606a"}

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

    def _render_icons(self) -> str:
        """Define reusable SVG symbols for icons."""
        return """
        <defs>
            <symbol id="icon-company" viewBox="0 0 16 16">
                <path fill="currentColor" d="M1.5 14.25c0 .138.112.25.25.25H4v-1.25a.75.75 0 0 1 .75-.75h2.5a.75.75 0 0 1 .75.75v1.25h2.25a.25.25 0 0 0 .25-.25V1.75a.25.25 0 0 0-.25-.25h-8.5a.25.25 0 0 0-.25.25v12.5zM1.75 16A1.75 1.75 0 0 1 0 14.25V1.75C0 .784.784 0 1.75 0h8.5C11.216 0 12 .784 12 1.75v12.5c0 .085-.006.168-.018.25h2.268a.25.25 0 0 0 .25-.25V8.285a.75.75 0 0 1 1.5 0v5.965A1.75 1.75 0 0 1 14.25 16H1.75zM6 13h1.5v3H6v-3zM2.75 4.5a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 0 1.5h-1.5a.75.75 0 0 1-.75-.75zm.75 2.25a.75.75 0 0 0 0 1.5h1.5a.75.75 0 0 0 0-1.5h-1.5zm0 3a.75.75 0 0 0 0 1.5h1.5a.75.75 0 0 0 0-1.5h-1.5zM8 4.5a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 0 1.5h-1.5a.75.75 0 0 1-.75-.75zm.75 2.25a.75.75 0 0 0 0 1.5h1.5a.75.75 0 0 0 0-1.5h-1.5zm0 3a.75.75 0 0 0 0 1.5h1.5a.75.75 0 0 0 0-1.5h-1.5z"></path>
            </symbol>
            <symbol id="icon-location" viewBox="0 0 16 16">
                <path fill="currentColor" d="M11.536 3.464a5 5 0 0 1 0 7.072L8 14.07l-3.536-3.535a5 5 0 1 1 7.072-7.072v.001zm1.06 8.132a6.5 6.5 0 1 0-9.192 0l3.535 3.536a1.5 1.5 0 0 0 2.122 0l3.535-3.536zM8 9a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"></path>
            </symbol>
            <symbol id="icon-link" viewBox="0 0 16 16">
                <path fill="currentColor" d="m7.775 3.275 1.25-1.25a3.5 3.5 0 1 1 4.95 4.95l-2.5 2.5a3.5 3.5 0 0 1-4.95 0 .751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018 1.998 1.998 0 0 0 2.83 0l2.5-2.5a2.002 2.002 0 0 0-2.83-2.83l-1.25 1.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042Zm-4.69 9.64a1.998 1.998 0 0 0 2.83 0l1.25-1.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-1.25 1.25a3.5 3.5 0 1 1-4.95-4.95l2.5-2.5a3.5 3.5 0 0 1 4.95 0 .751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018 1.998 1.998 0 0 0-2.83 0l-2.5 2.5a1.998 1.998 0 0 0 0 2.83Z"></path>
            </symbol>
            <symbol id="icon-star" viewBox="0 0 16 16">
                <path fill="currentColor" d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path>
            </symbol>
            <symbol id="icon-repo" viewBox="0 0 16 16">
                <path fill="currentColor" d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"></path>
            </symbol>
            <symbol id="icon-commit" viewBox="0 0 16 16">
                <path fill="currentColor" d="M11.93 8.5a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4.002 4.002 0 0 1 7.86 0h3.32a.75.75 0 0 1 0 1.5Zm-1.43-.75a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z"></path>
            </symbol>
            <symbol id="icon-users" viewBox="0 0 16 16">
                <path fill="currentColor" d="M2 5.5a3.5 3.5 0 1 1 5.898 2.549 5.508 5.508 0 0 1 3.034 4.084.75.75 0 1 1-1.482.235 4 4 0 0 0-7.9 0 .75.75 0 0 1-1.482-.236A5.507 5.507 0 0 1 3.102 8.05 3.493 3.493 0 0 1 2 5.5ZM11 4a3.001 3.001 0 0 1 2.22 5.018 5.01 5.01 0 0 1 2.56 3.012.75.75 0 0 1-1.41.54 3.5 3.5 0 0 0-1.902-2.203.75.75 0 0 1 .132-1.465A1.5 1.5 0 1 0 11 5.5a.75.75 0 0 1-1.5 0c0-.828.672-1.5 1.5-1.5Z"></path>
            </symbol>
        </defs>
        """

    def _render_profile_info(self, colors: dict[str, str], current_y: int) -> tuple[str, int]:
        """Render the top header including bio and links."""
        name = self.profile.get("name", "Unknown")
        username = self.profile.get("username", "")
        bio = self.profile.get("bio", "")

        svg = f"""
        <text x="0" y="{current_y}" font-size="32" font-weight="bold" fill="{colors['text']}">{name}</text>
        """
        if username:
            svg += f'<text x="0" y="{current_y + 28}" font-size="20" fill="{colors["secondary"]}">@{username}</text>'
        
        current_y += 64
        
        if bio:
            words = bio.split(" ")
            line = ""
            for word in words:
                # Approximate text wrapping for ~70 chars
                if len(line) + len(word) > 70:
                    svg += f'<text x="0" y="{current_y}" font-size="16" fill="{colors["text"]}">{line}</text>\n'
                    current_y += 24
                    line = word + " "
                else:
                    line += word + " "
            if line:
                svg += f'<text x="0" y="{current_y}" font-size="16" fill="{colors["text"]}">{line.strip()}</text>\n'
                current_y += 24
                
        current_y += 16
        
        # Details (Company, Location, Website)
        details = []
        if self.profile.get("company"):
            details.append(("icon-company", self.profile["company"]))
        if self.profile.get("location"):
            details.append(("icon-location", self.profile["location"]))
        if self.profile.get("website"):
            details.append(("icon-link", self.profile["website"]))
            
        for icon, text in details:
            svg += f"""
            <use href="#{icon}" x="0" y="{current_y-12}" width="16" height="16" fill="{colors['secondary']}" />
            <text x="24" y="{current_y}" font-size="14" fill="{colors['text']}">{text}</text>
            """
            current_y += 24
            
        return svg, current_y + 20

    def _render_skills(self, colors: dict[str, str], current_y: int) -> tuple[str, int]:
        """Render the dynamic skills layout."""
        if not any(self.skills.values()):
            return "", current_y

        svg = f"""
        <text x="0" y="{current_y}" font-size="22" font-weight="bold" fill="{colors['text']}">Skills &amp; Technologies</text>
        <line x1="0" y1="{current_y + 12}" x2="{self.right_panel_width}" y2="{current_y + 12}" stroke="{colors['secondary']}" stroke-opacity="0.3" stroke-width="1"/>
        """
        current_y += 36
        
        for category, skill_list in self.skills.items():
            if not skill_list:
                continue
            cat_name = category.replace("_", " ").title()
            svg += f'<text x="0" y="{current_y}" font-size="16" font-weight="bold" fill="{colors["primary"]}">{cat_name}</text>\n'
            current_y += 24
            
            x_offset = 0
            for skill in skill_list:
                # Estimate width: ~8px per char + 20px padding
                skill_width = len(skill) * 8 + 20
                if x_offset + skill_width > self.right_panel_width:
                    x_offset = 0
                    current_y += 32
                
                svg += f"""
                <rect x="{x_offset}" y="{current_y - 18}" width="{skill_width}" height="26" rx="4" fill="{colors['primary']}" fill-opacity="0.1" stroke="{colors['primary']}" stroke-opacity="0.3" stroke-width="1"/>
                <text x="{x_offset + 10}" y="{current_y}" font-size="13" fill="{colors['text']}">{skill}</text>
                """
                x_offset += skill_width + 10
            current_y += 40
            
        return svg, current_y

    def _render_stats(self, colors: dict[str, str], current_y: int) -> tuple[str, int]:
        """Render the key GitHub statistics in a grid."""
        if not self.stats:
            return "", current_y

        svg = f"""
        <text x="0" y="{current_y}" font-size="22" font-weight="bold" fill="{colors['text']}">GitHub Statistics</text>
        <line x1="0" y1="{current_y + 12}" x2="{self.right_panel_width}" y2="{current_y + 12}" stroke="{colors['secondary']}" stroke-opacity="0.3" stroke-width="1"/>
        """
        current_y += 36
        
        # Read from stats engine payload
        stats_data = [
            ("icon-repo", "Public Repositories", str(self.stats.get("repositories", {}).get("public_repository_count", 0))),
            ("icon-star", "Total Stars", str(self.stats.get("stars", {}).get("total_stars", 0))),
            ("icon-commit", "Total Commits", str(self.stats.get("commits", {}).get("total_commits", 0))),
            ("icon-users", "Followers", str(self.stats.get("profile", {}).get("total_followers", 0)))
        ]
        
        box_width = 270
        box_height = 50
        
        for i, (icon, label, value) in enumerate(stats_data):
            col = i % 2
            row = i // 2
            
            x = col * (box_width + 20)
            y = current_y + row * (box_height + 16)
            
            svg += f"""
            <rect x="{x}" y="{y}" width="{box_width}" height="{box_height}" rx="6" fill="{colors['secondary']}" fill-opacity="0.05" stroke="{colors['secondary']}" stroke-opacity="0.2" stroke-width="1"/>
            <use href="#{icon}" x="{x + 16}" y="{y + 17}" width="16" height="16" fill="{colors['primary']}" />
            <text x="{x + 44}" y="{y + 29}" font-size="14" font-weight="bold" fill="{colors['text']}">{label}</text>
            <text x="{x + box_width - 16}" y="{y + 29}" font-size="16" font-weight="bold" fill="{colors['primary']}" text-anchor="end">{value}</text>
            """
            
        rows = len(stats_data) // 2 + (1 if len(stats_data) % 2 else 0)
        return svg, current_y + (rows * (box_height + 16)) + 20

    def _render_featured_projects(self, colors: dict[str, str], current_y: int) -> tuple[str, int]:
        """Render featured projects if they exist."""
        projects = self.stats.get("featured_projects", [])
        if not projects:
            return "", current_y
            
        svg = f"""
        <text x="0" y="{current_y}" font-size="22" font-weight="bold" fill="{colors['text']}">Featured Projects</text>
        <line x1="0" y1="{current_y + 12}" x2="{self.right_panel_width}" y2="{current_y + 12}" stroke="{colors['secondary']}" stroke-opacity="0.3" stroke-width="1"/>
        """
        current_y += 36
        
        for proj in projects[:3]: # limit to 3 projects to avoid huge SVGs
            name = proj.get("name", "Unknown")
            desc = proj.get("description", "") or "No description provided."
            lang = proj.get("language", "")
            stars = proj.get("stars", 0)
            
            # Box background
            svg += f"""
            <rect x="0" y="{current_y}" width="{self.right_panel_width}" height="70" rx="6" fill="{colors['secondary']}" fill-opacity="0.05" stroke="{colors['secondary']}" stroke-opacity="0.2" stroke-width="1"/>
            <use href="#icon-repo" x="16" y="{current_y + 16}" width="16" height="16" fill="{colors['primary']}" />
            <text x="40" y="{current_y + 28}" font-size="16" font-weight="bold" fill="{colors['primary']}">{name}</text>
            """
            
            # Simple text truncation
            if len(desc) > 65:
                desc = desc[:62] + "..."
            svg += f'<text x="40" y="{current_y + 52}" font-size="13" fill="{colors["secondary"]}">{desc}</text>'
            
            # Language dot and name
            if lang:
                svg += f"""
                <circle cx="450" cy="{current_y + 24}" r="5" fill="{colors['text']}" fill-opacity="0.5"/>
                <text x="462" y="{current_y + 28}" font-size="12" fill="{colors['secondary']}">{lang}</text>
                """
            # Stars
            svg += f"""
            <use href="#icon-star" x="510" y="{current_y + 17}" width="14" height="14" fill="{colors['secondary']}" />
            <text x="528" y="{current_y + 28}" font-size="12" fill="{colors['secondary']}">{stars}</text>
            """
            
            current_y += 82
            
        return svg, current_y + 20

    def render(self) -> None:
        """Execute the dynamic layout engine and render SVGs."""
        logger.info("--- PHASE 05: SVG RENDERER STARTED ---")
        
        for mode in ["light", "dark"]:
            logger.info(f"Generating {mode} theme layout...")
            colors = self._get_theme_colors(mode)
            ascii_content = self._get_ascii_svg_content(mode)
            
            right_panel_svg = ""
            current_y = 50
            
            p_svg, current_y = self._render_profile_info(colors, current_y)
            right_panel_svg += p_svg
            
            s_svg, current_y = self._render_skills(colors, current_y)
            right_panel_svg += s_svg
            
            st_svg, current_y = self._render_stats(colors, current_y)
            right_panel_svg += st_svg
            
            fp_svg, current_y = self._render_featured_projects(colors, current_y)
            right_panel_svg += fp_svg
            
            # Generate Footer
            now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
            footer_y = max(current_y + 40, self.min_height - 40)
            
            right_panel_svg += f"""
            <line x1="0" y1="{footer_y - 20}" x2="{self.right_panel_width}" y2="{footer_y - 20}" stroke="{colors['secondary']}" stroke-opacity="0.2" stroke-width="1"/>
            <text x="0" y="{footer_y}" font-size="12" fill="{colors['secondary']}">Generated automatically by EL-STRIX Engine • Last Updated: {now}</text>
            """
            
            final_height = max(self.min_height, footer_y + 30)
            
            # Master SVG Template
            svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {final_height}" width="{self.width}" height="{final_height}">
    <!-- Background -->
    <rect width="100%" height="100%" fill="{colors['background']}" rx="12"/>
    
    <style>
        text {{
            font-family: {self.font_family};
        }}
        .ascii-text {{ 
            font-family: monospace; 
            font-size: 12px; 
            fill: {colors['text']}; 
            white-space: pre; 
        }}
    </style>
    
    {self._render_icons()}
    
    <!-- Left Panel (ASCII Avatar) -->
    <g transform="translate(20, 20)">
        <g class="ascii-text">
            {ascii_content}
        </g>
    </g>

    <!-- Right Panel (Profile and Statistics) -->
    <g transform="translate({self.left_panel_width + 40}, 0)">
        {right_panel_svg}
    </g>
</svg>"""
            
            output_path = os.path.join(self.output_dir, f"{mode}.svg")
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(svg)
                logger.info(f"Rendered dynamic SVG layout: {output_path}")
            except Exception as e:
                logger.error(f"Failed to write SVG {mode}: {e}")

        logger.info("--- PHASE 05 COMPLETED ---")
