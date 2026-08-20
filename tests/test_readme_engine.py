import os
import sys

# Add scripts directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))

from readme_engine import ReadmeEngine


def test_autoescape_enabled(mocker, tmp_path) -> None:
    """Test that Jinja2 autoescape is enabled to prevent XSS/HTML injection."""
    # Create a mock template directory and file
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_file = template_dir / "README.template.md"
    template_file.write_text("Bio: {{ bio }}")

    # Mock PathManager to use our temporary directory
    mocker.patch("readme_engine.PathManager.TEMPLATES_DIR", new=template_dir)
    # Also mock ROOT_DIR to avoid any file creation side effects in real path
    mocker.patch("readme_engine.PathManager.ROOT_DIR", new=tmp_path)

    # Instantiate the engine
    engine = ReadmeEngine()

    # Mock _prepare_data to return a context with a malicious payload
    malicious_payload = "<script>alert(1)</script>"
    mocker.patch.object(engine, "_prepare_data", return_value={"bio": malicious_payload})

    # Render the template
    content = engine.render()

    # Assert that the output is properly escaped
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in content
    assert "<script>" not in content
