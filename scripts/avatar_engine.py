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
            img = Image.open(image_path)
            
            # Composite over white background to handle transparency correctly
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img = img.convert('RGBA')
                bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img = bg
                
            img = img.convert("L")  # Grayscale
            
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
        
    def generate_matrix(self, img: Image.Image) -> list[list[str]]:
        """Generate a reusable ASCII matrix."""
        # Calculate height based on font aspect ratio (~0.55 usually)
        aspect_ratio = img.height / img.width
        font_aspect_correction = self.config.get("font_aspect_correction", 0.55)
        height = int(self.width * aspect_ratio * font_aspect_correction)
        
        resample_filter = Image.Resampling.LANCZOS
        img_resized = img.resize((self.width, height), resample_filter)
        pixels = list(img_resized.getdata())  # type: ignore
        
        char_count = len(self.charset)
        matrix = []
        
        # 1. Detect Background Brightness by sampling the 4 corners
        corners = [
            pixels[0],                                           # Top-left
            pixels[self.width - 1],                              # Top-right
            pixels[(height - 1) * self.width],                   # Bottom-left
            pixels[(height - 1) * self.width + (self.width - 1)] # Bottom-right
        ]
        bg_val = sum(corners) / 4.0
        
        # 2. Determine Image Type & Dynamic Mapping
        is_bright_bg = bg_val > 127
        
        for i in range(height):
            row = []
            for j in range(self.width):
                pixel_val = pixels[i * self.width + j]
                
                if is_bright_bg:
                    # Case: Dark Subject on Bright Background
                    # Force background to be pure white (empty space)
                    if pixel_val >= bg_val - 25:
                        pixel_val = 255
                    
                    # Mapping: Dark (0) -> Dense (9), Bright (255) -> Empty (0)
                    raw_idx = int((pixel_val / 255.0) * (char_count - 1))
                    char_idx = (char_count - 1) - raw_idx
                else:
                    # Case: Bright Subject on Dark Background
                    # Force background to be pure black (empty space)
                    if pixel_val <= bg_val + 25:
                        pixel_val = 0
                        
                    # Mapping: Dark (0) -> Empty (0), Bright (255) -> Dense (9)
                    char_idx = int((pixel_val / 255.0) * (char_count - 1))
                    
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
        
        # For dark mode, invert the characters so the polarity of the image is preserved
        charset = self.ascii_config.get("charset", " .:-=+*#%@")
        if mode == "dark":
            char_map = {c: charset[len(charset) - 1 - i] for i, c in enumerate(charset)}
            processed_matrix = [[char_map.get(c, c) for c in row] for row in matrix]
        else:
            processed_matrix = matrix
        
        y_offset = self.font_size
        for row in processed_matrix:
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
            
        # 2. Ascii Matrix
        matrix = self.ascii_engine.generate_matrix(img)
        
        # Save matrix
        matrix_path = PathManager.ASSET_ASCII_DIR / "matrix.json"
        try:
            with open(matrix_path, "w", encoding="utf-8") as f:
                json.dump(matrix, f)
            logger.info(f"ASCII matrix saved to {matrix_path}")
        except Exception as e:
            logger.error(f"Failed to save ASCII matrix: {e}")
            return
            
        # 3. SVG Rendering
        PathManager.ensure_directories()
        
        light_svg_path = PathManager.GENERATED_SVG_DIR / "avatar_light.svg"
        dark_svg_path = PathManager.GENERATED_SVG_DIR / "avatar_dark.svg"
        
        success_light = self.svg_renderer.render(matrix, "light", light_svg_path)
        success_dark = self.svg_renderer.render(matrix, "dark", dark_svg_path)
        
        if success_light and success_dark:
            logger.info("Avatar SVGs generated successfully.")
            # Update cache hash
            with open(cache_file, "w") as f:
                f.write(current_hash)
        else:
            logger.error("Failed to generate avatar SVGs.")
            
        logger.info("--- PHASE 04 COMPLETED ---")
