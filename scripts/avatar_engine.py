"""
Avatar Processing Engine
Handles image validation, professional preprocessing, ASCII matrix generation, and SVG rendering.
"""

import hashlib
import json
import math
from pathlib import Path
from typing import Any, cast

from config_loader import ConfigLoader
from logger import logger
from paths import PathManager
from PIL import Image, ImageFilter, ImageOps, ImageStat


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
                img.verify()
                return True

        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False


class ImagePreprocessor:
    """Professional preprocessing pipeline for Computer Vision ASCII optimization."""

    def __init__(self, settings: dict[str, Any]):
        self.config = settings.get("avatar_preprocessing", {})

    def _apply_gamma(self, img: Image.Image, gamma: float = 1.0) -> Image.Image:
        """Apply non-linear gamma scaling."""
        inv_gamma = 1.0 / gamma
        table = [int((i / 255.0) ** inv_gamma * 255) for i in range(256)]

        if img.mode == "L":
            return img.point(table)
        elif img.mode == "RGB":
            r, g, b = img.split()
            return Image.merge("RGB", (r.point(table), g.point(table), b.point(table)))
        elif img.mode == "RGBA":
            r, g, b, a = img.split()
            return Image.merge("RGBA", (r.point(table), g.point(table), b.point(table), a))
        return img

    def _extract_subject_mask(self, img: Image.Image) -> Image.Image:
        """Create a mask isolating the subject from the background using rembg with fallback."""
        try:
            import rembg

            return cast(Image.Image, rembg.remove(img, only_mask=True))
        except Exception as e:
            logger.warning(f"rembg background removal unavailable ({e}). Using luminance mask fallback.")
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                return img.convert("RGBA").split()[-1]
            return Image.new("L", img.size, 255)

    def process(self, image_path: Path) -> dict[str, Image.Image] | None:
        try:
            img = Image.open(image_path)

            # 1. EXIF correction
            img = ImageOps.exif_transpose(img)

            # 2. Alpha handling & Background separation
            mask = self._extract_subject_mask(img)
            img = img.convert("RGBA")

            # Crop to subject bounding box to remove empty space
            bbox = mask.getbbox()
            if bbox:
                img = img.crop(bbox)
                mask = mask.crop(bbox)

                # Add minimal dynamic padding (2% on each side) to maximize subject size without overlap
                w, h = img.size
                pad_w = int(w * 0.02)
                pad_h = int(h * 0.02)

                new_w = w + 2 * pad_w
                new_h = h + 2 * pad_h

                padded_img = Image.new("RGBA", (new_w, new_h), (255, 255, 255, 0))
                padded_mask = Image.new("L", (new_w, new_h), 0)

                padded_img.paste(img, (pad_w, pad_h))
                padded_mask.paste(mask, (pad_w, pad_h))

                img = padded_img
                mask = padded_mask

            # Extract subject RGB onto a solid background for processing
            subject_rgb = Image.new("RGB", img.size, (255, 255, 255))
            subject_rgb.paste(img, mask=mask)

            # 3 & 4. Auto contrast & Histogram Equalization (Local Contrast)
            # Equalize the luminance while preserving color
            hsv = subject_rgb.convert("HSV")
            h, s, v = hsv.split()

            # Smart equalization on Value channel
            v_eq = ImageOps.equalize(v)
            # Blend equalized with original to avoid aggressive artifacts (CLAHE approximation)
            v = Image.blend(v, v_eq, alpha=0.6)

            hsv = Image.merge("HSV", (h, s, v))
            subject_rgb = hsv.convert("RGB")

            # 5. Gamma correction & Adaptive brightness
            stat = ImageStat.Stat(subject_rgb.convert("L"), mask=mask)
            mean_lum = stat.mean[0]  # Luminance of subject

            target_lum = 128
            if mean_lum > 0:
                gamma = math.log(target_lum / 255.0) / math.log(mean_lum / 255.0)
                # Keep gamma within reasonable bounds to prevent blowout
                gamma = max(0.5, min(2.0, gamma))
                subject_rgb = self._apply_gamma(subject_rgb, gamma)

            # 6. Noise reduction & Adaptive sharpening
            subject_rgb = subject_rgb.filter(ImageFilter.MedianFilter(size=3))
            subject_rgb = subject_rgb.filter(
                ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)
            )

            # 7. Edge Enhancement for structural preservation
            edges = subject_rgb.convert("L").filter(ImageFilter.FIND_EDGES)
            # Dilate edges slightly so structural lines are highly pronounced
            edges = edges.filter(ImageFilter.MaxFilter(3))

            return {"rgb": subject_rgb, "mask": mask, "edges": edges}
        except Exception as e:
            logger.error(f"Professional preprocessing failed: {e}")
            return None


class AsciiEngine:
    """Professional ASCII Matrix Generation with structural edge-mapping."""

    def __init__(self, settings: dict[str, Any]):
        self.config = settings.get("ascii_engine", {})
        # Clean, recognizable 10-character density ramp
        self.charset = "@%#*+=-:. "
        self.char_count = len(self.charset)
        self.width = self.config.get("width", 85)

    def get_perceptual_luminance(self, r: int, g: int, b: int) -> float:
        """Calculate human-perceptual luminance using weighted Euclidean distance."""
        return math.sqrt(0.299 * r**2 + 0.587 * g**2 + 0.114 * b**2)

    def generate_matrix(self, processed_data: dict[str, Image.Image]) -> list[list[str]]:
        """Generate ONE master ASCII matrix compatible with both Light and Dark modes."""
        rgb_img = processed_data["rgb"]
        mask_img = processed_data["mask"]
        edges_img = processed_data["edges"]

        # 1. Font Aspect Ratio Calibration (standard monospace aspect ratio is ~0.5)
        aspect_ratio = rgb_img.height / rgb_img.width
        font_aspect_correction = self.config.get("font_aspect_correction", 0.5)
        height = int(self.width * aspect_ratio * font_aspect_correction)

        resample_filter = Image.Resampling.LANCZOS
        rgb_resized = rgb_img.resize((self.width, height), resample_filter)
        mask_resized = mask_img.resize((self.width, height), resample_filter)
        edges_resized = edges_img.resize((self.width, height), resample_filter)

        rgb_pixels = list(rgb_resized.getdata())  # type: ignore
        mask_pixels = list(mask_resized.getdata())  # type: ignore
        edges_pixels = list(edges_resized.getdata())  # type: ignore

        char_count_minus_1 = self.char_count - 1
        charset = self.charset

        flat_chars = []
        for (r, g, b), m, e in zip(rgb_pixels, mask_pixels, edges_pixels):
            if m < 128:
                # Transparent Background -> Space (sparsest character)
                char_idx = char_count_minus_1
            else:
                # Inlined perceptual luminance calculation for speed
                lum = math.sqrt(0.299 * r**2 + 0.587 * g**2 + 0.114 * b**2)

                # Normalize lum to 0-1
                norm_lum = lum / 255.0

                # Clean contrast curve to keep face recognizable and avoid noise
                gamma_lum = norm_lum**0.8
                final_density = (1.0 - gamma_lum) * 0.5 + (e / 255.0) * 0.5

                # Force eyes and dark hair to remain dense
                if norm_lum < 0.25:
                    final_density = max(final_density, 0.8)

                # Map to character index (0 is densest, char_count-1 is sparsest)
                char_idx = int((1.0 - final_density) * char_count_minus_1)
                char_idx = max(0, min(char_count_minus_1, char_idx))

            flat_chars.append(charset[char_idx])

        # Reform into 2D matrix
        matrix = [flat_chars[i : i + self.width] for i in range(0, len(flat_chars), self.width)]

        return matrix


class AvatarSvgRenderer:
    """Renders the single master ASCII matrix into an SVG file."""

    def __init__(self, theme: dict[str, Any], settings: dict[str, Any]):
        self.theme = theme
        self.config = settings.get("svg_engine", {})
        self.font_family = self.config.get("font_family", "Consolas, 'Courier New', monospace")
        self.font_size = self.config.get("font_size", 14)
        self.line_spacing = self.config.get("line_spacing", 1.2)
        self.char_spacing = self.config.get("char_spacing", 0.6)

    def render(self, matrix: list[list[str]], mode: str, output_path: Path) -> bool:
        """Render matrix to SVG based on light or dark mode theme colors."""
        if not matrix or not matrix[0]:
            logger.warning("ASCII matrix is empty. Skipping SVG render.")
            return False

        colors = self.theme.get(mode, {})
        # Optimize contrast for GitHub themes
        bg_color = colors.get("background", "#0d1117" if mode == "dark" else "#ffffff")
        text_color = colors.get("text", "#c9d1d9" if mode == "dark" else "#24292f")

        height_px = len(matrix) * self.font_size * self.line_spacing
        width_px = len(matrix[0]) * self.font_size * self.char_spacing

        svg_content = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_px} {height_px}" width="{width_px}" height="{height_px}">',
            f'<rect width="100%" height="100%" fill="{bg_color}" rx="8"/>',
            "<style>",
            f"  .ascii-text {{ font-family: {self.font_family}; font-size: {self.font_size}px; fill: {text_color}; white-space: pre; }}",
            "</style>",
            '<g class="ascii-text">',
        ]

        y_offset = self.font_size
        for row in matrix:
            line_str = "".join(row).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            svg_content.append(f'  <text x="0" y="{y_offset}">{line_str}</text>')
            y_offset += self.font_size * self.line_spacing

        svg_content.append("</g>")
        svg_content.append("</svg>")

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(svg_content))
            return True
        except OSError as e:
            logger.error(f"Failed to write SVG to {output_path}: {e}")
            return False


class AvatarPipeline:
    """Orchestrator for the Advanced Avatar Processing Engine."""

    def __init__(self):
        self.configs = ConfigLoader.load_all()
        self.settings = self.configs.get("settings", {})
        self.theme = self.configs.get("theme", {})

        self.image_validator = ImageValidator()
        self.preprocessor = ImagePreprocessor(self.settings)
        self.ascii_engine = AsciiEngine(self.settings)
        self.svg_renderer = AvatarSvgRenderer(self.theme, self.settings)

    def _get_image_hash(self, image_path: Path) -> str:
        """Calculate SHA256 hash of the image for caching purposes."""
        hash_sha256 = hashlib.sha256()
        with open(image_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

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

        logger.info("Avatar changes detected. Processing new avatar with advanced CV pipeline...")

        # 1. Professional Preprocess
        processed_data = self.preprocessor.process(avatar_path)
        if not processed_data:
            logger.error("Avatar preprocessing failed.")
            return

        # 2. Master Ascii Matrix
        master_matrix = self.ascii_engine.generate_matrix(processed_data)

        # Save matrix
        matrix_path = PathManager.ASSET_ASCII_DIR / "matrix.json"
        try:
            with open(matrix_path, "w", encoding="utf-8") as f:
                json.dump(master_matrix, f)
            logger.info(f"Master ASCII matrix saved to {matrix_path}")
        except Exception as e:
            logger.error(f"Failed to save ASCII matrix: {e}")
            return

        # 3. SVG Rendering
        PathManager.ensure_directories()

        light_svg_path = PathManager.GENERATED_SVG_DIR / "avatar_light.svg"
        dark_svg_path = PathManager.GENERATED_SVG_DIR / "avatar_dark.svg"

        success_light = self.svg_renderer.render(master_matrix, "light", light_svg_path)
        success_dark = self.svg_renderer.render(master_matrix, "dark", dark_svg_path)

        if success_light and success_dark:
            logger.info("Avatar SVGs generated successfully.")
            with open(cache_file, "w") as f:
                f.write(current_hash)
        else:
            logger.error("Failed to generate avatar SVGs.")

        logger.info("--- PHASE 04 COMPLETED ---")
