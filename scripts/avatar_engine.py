"""
Avatar Processing Engine
Handles image validation, preprocessing, ASCII matrix generation, and SVG rendering.
"""

import hashlib
import json
from pathlib import Path
from typing import Any

from config_loader import ConfigLoader
from exceptions import ELSTRIXError
from logger import logger
from paths import PathManager
from PIL import Image, ImageEnhance


class AvatarProcessingError(ELSTRIXError):
    """Exception raised for errors in the Avatar Processing Engine."""

class ImageValidator:
    """Validates the downloaded avatar image."""
    
    SUPPORTED_FORMATS = ["JPEG", "PNG", "WEBP", "MPO"]
    MIN_DIMENSIONS = (50, 50)
    MAX_DIMENSIONS = (4096, 4096)
    
    @classmethod
    def validate(cls, image_path: Path) -> bool:
        if not image_path.exists() or not image_path.is_file():
            logger.error(f"Image not found at {image_path}")
            return False
            
        try:
            with Image.open(image_path) as img:
                # Some web formats might be missing the format attribute when opened via stream in previous phases
                # But it's generally safe. Let's just check if it can be verified.
                img.verify()
                return True
                
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False

class ImagePreprocessor:
    """Preprocesses the image for ASCII conversion."""
    
    def __init__(self, settings: dict[str, Any]):
        self.config = settings.get("avatar_preprocessing", {})
        self.contrast = self.config.get("contrast", 1.2)
        self.brightness = self.config.get("brightness", 1.0)
        self.sharpness = self.config.get("sharpness", 1.5)
        
    def process(self, image_path: Path) -> Image.Image | None:
        try:
            img = Image.open(image_path).convert('RGBA')
            
            # Enhancements
            if self.contrast != 1.0:
                img = ImageEnhance.Contrast(img).enhance(self.contrast)
            if self.brightness != 1.0:
                img = ImageEnhance.Brightness(img).enhance(self.brightness)
            if self.sharpness != 1.0:
                img = ImageEnhance.Sharpness(img).enhance(self.sharpness)
                
            return img
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            return None

class AsciiEngine:
    """Converts a preprocessed image into an ASCII matrix."""
    
    def __init__(self, settings: dict[str, Any]):
        self.config = settings.get("ascii_engine", {})
        self.charset = self.config.get("charset", " .:-=+*#%@")
        self.width = self.config.get("width", 80)
        
    def generate_matrix(self, img: Image.Image, mode: str) -> list[list[str]]:
        """Generate a theme-aware ASCII matrix."""
        aspect_ratio = img.height / img.width
        font_aspect_correction = self.config.get("font_aspect_correction", 0.55)
        height = int(self.width * aspect_ratio * font_aspect_correction)
        
        resample_filter = Image.Resampling.LANCZOS
        img_resized = img.resize((self.width, height), resample_filter)
        pixels = list(img_resized.getdata())  # type: ignore
        
        char_count = len(self.charset)
        matrix = []
        
        # 1. Detect Background Brightness from 4 corners
        corners = [
            pixels[0], pixels[self.width - 1],
            pixels[(height - 1) * self.width], pixels[(height - 1) * self.width + (self.width - 1)]
        ]
        
        opaque_corners = [c for c in corners if c[3] > 128]
        if opaque_corners:
            bg_lum = sum((0.299*c[0] + 0.587*c[1] + 0.114*c[2]) for c in opaque_corners) / len(opaque_corners)
        else:
            bg_lum = None
            
        for i in range(height):
            row = []
            for j in range(self.width):
                r, g, b, a = pixels[i * self.width + j]
                lum = 0.299*r + 0.587*g + 0.114*b
                
                is_bg = False
                if a < 128:
                    is_bg = True
                elif bg_lum is not None:
                    if bg_lum > 127 and lum >= bg_lum - 15:
                        is_bg = True
                    elif bg_lum <= 127 and lum <= bg_lum + 15:
                        is_bg = True
                        
                if is_bg:
                    char_idx = 0
                else:
                    if mode == "light":
                        char_idx = int(((255 - lum) / 255.0) * (char_count - 1))
                    else:
                        char_idx = int((lum / 255.0) * (char_count - 1))
                        
                char_idx = max(0, min(char_count - 1, char_idx))
                row.append(self.charset[char_idx])
            matrix.append(row)
            
        return matrix

class AvatarSvgRenderer:
    """Renders the ASCII matrix into an SVG file."""
    
    def __init__(self, theme: dict[str, Any], settings: dict[str, Any]):
        self.theme = theme
        self.config = settings.get("svg_engine", {})
        self.ascii_config = settings.get("ascii_engine", {})
        self.font_family = self.config.get("font_family", "monospace")
        self.font_size = self.config.get("font_size", 12)
        self.line_spacing = self.config.get("line_spacing", 1.2)
        self.char_spacing = self.config.get("char_spacing", 0.6)
        
    def render(self, matrix: list[list[str]], mode: str, output_path: Path) -> bool:
        """Render matrix to SVG based on light or dark mode."""
        colors = self.theme.get(mode, {})
        bg_color = colors.get("background", "#000000" if mode == "dark" else "#ffffff")
        text_color = colors.get("text", "#ffffff" if mode == "dark" else "#000000")
        
        height_px = len(matrix) * self.font_size * self.line_spacing
        width_px = len(matrix[0]) * self.font_size * self.char_spacing
        
        svg_content = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_px} {height_px}" width="{width_px}" height="{height_px}">',
            f'<rect width="100%" height="100%" fill="{bg_color}"/>',
            '<style>',
            f'  .ascii-text {{ font-family: {self.font_family}; font-size: {self.font_size}px; fill: {text_color}; white-space: pre; }}',
            '</style>',
            '<g class="ascii-text">'
        ]
        
        y_offset = self.font_size
        for row in matrix:
            line_str = "".join(row).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            svg_content.append(f'  <text x="0" y="{y_offset}">{line_str}</text>')
            y_offset += self.font_size * self.line_spacing
            
        svg_content.append('</g>')
        svg_content.append('</svg>')
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(svg_content))
            return True
        except OSError as e:
            logger.error(f"Failed to write SVG to {output_path}: {e}")
            return False

class AvatarPipeline:
    """Orchestrator for the Avatar Processing Engine."""
    
    def __init__(self):
        self.configs = ConfigLoader.load_all()
        self.settings = self.configs.get("settings", {})
        self.theme = self.configs.get("theme", {})
        
        self.image_validator = ImageValidator()
        self.preprocessor = ImagePreprocessor(self.settings)
        self.ascii_engine = AsciiEngine(self.settings)
        self.svg_renderer = AvatarSvgRenderer(self.theme, self.settings)
        
    def _get_image_hash(self, image_path: Path) -> str:
        """Calculate MD5 hash of the image for caching purposes."""
        hash_md5 = hashlib.md5()
        with open(image_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def run(self) -> None:
        """Execute the full avatar pipeline."""
        logger.info("--- PHASE 04: AVATAR PROCESSING PIPELINE ---")
        
        avatar_path = PathManager.ASSET_IMAGE_DIR / "avatar.png"
        
        if not self.image_validator.validate(avatar_path):
            logger.warning("Avatar validation failed or missing. Skipping Phase 04.")
            return
            
        # Check cache
        cache_file = PathManager.GENERATED_CACHE_DIR / "avatar_hash.txt"
        current_hash = self._get_image_hash(avatar_path)
        
        if cache_file.exists():
            with open(cache_file, "r") as f:
                cached_hash = f.read().strip()
            if cached_hash == current_hash:
                logger.info("Avatar unchanged. Using cached ASCII matrix and SVGs.")
                logger.info("--- PHASE 04 COMPLETED ---")
                return
                
        logger.info("Avatar changes detected. Processing new avatar...")
        
        # 1. Preprocess
        img = self.preprocessor.process(avatar_path)
        if not img:
            logger.error("Avatar preprocessing failed.")
            return
            
        # 2. Ascii Matrix (Theme Aware)
        matrix_light = self.ascii_engine.generate_matrix(img, "light")
        matrix_dark = self.ascii_engine.generate_matrix(img, "dark")
        
        # Save matrices
        matrix_path = PathManager.ASSET_ASCII_DIR / "matrix.json"
        try:
            with open(matrix_path, "w", encoding="utf-8") as f:
                json.dump({"light": matrix_light, "dark": matrix_dark}, f)
            logger.info(f"ASCII matrices saved to {matrix_path}")
        except Exception as e:
            logger.error(f"Failed to save ASCII matrices: {e}")
            return
            
        # 3. SVG Rendering
        PathManager.ensure_directories()
        
        light_svg_path = PathManager.GENERATED_SVG_DIR / "avatar_light.svg"
        dark_svg_path = PathManager.GENERATED_SVG_DIR / "avatar_dark.svg"
        
        success_light = self.svg_renderer.render(matrix_light, "light", light_svg_path)
        success_dark = self.svg_renderer.render(matrix_dark, "dark", dark_svg_path)
        
        if success_light and success_dark:
            logger.info("Avatar SVGs generated successfully.")
            # Update cache hash
            with open(cache_file, "w") as f:
                f.write(current_hash)
        else:
            logger.error("Failed to generate avatar SVGs.")
            
        logger.info("--- PHASE 04 COMPLETED ---")
