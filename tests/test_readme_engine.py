from scripts.readme_engine import ReadmeEngine


def test_readme_engine_autoescape():
    engine = ReadmeEngine()
    assert engine.env.autoescape == True
