"""Main entry point for EL-STRIX profile and banner updates."""

import sys

from config_loader import ConfigLoader
from data_engine import DataEngine
from env import EnvManager
from exceptions import ELSTRIXError
from logger import logger, setup_logger

# Initialize Foundation
from paths import PathManager


def initialize() -> None:
    """Initialize the EL-STRIX engine foundation."""
    logger.info("Initializing EL-STRIX foundation...")
    
    try:
        # 1. Ensure all core directories exist
        PathManager.ensure_directories()
        logger.debug("Directory structure verified.")
        
        # 2. Load and validate environment variables
        EnvManager.load()
        username = EnvManager.get_github_username()
        logger.debug(f"Environment loaded for user: {username}")
        
        # 3. Load configuration files
        configs = ConfigLoader.load_all()
        settings = configs.get("settings", {})
        
        # Re-configure logger if debug mode is enabled in settings
        if settings.get("debug_mode"):
            setup_logger(debug_mode=True)
            logger.debug("Debug mode enabled.")
            
        logger.info("Configuration files loaded successfully.")
        
    except ELSTRIXError as e:
        logger.error(f"Initialization Failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error during initialization: {e}", exc_info=True)
        sys.exit(1)

def run_phase_02():
    """Execute Phase 02: GitHub Data Engine."""
    try:
        logger.info("--- PHASE 02: GITHUB DATA ENGINE ---")
        engine = DataEngine()
        engine.run_all()
        logger.info("--- PHASE 02 COMPLETED ---")
    except ELSTRIXError as e:
        logger.warning(f"Phase 02 Skipped: {e}")
        logger.warning("Renderer will use previously cached statistics if available.")
    except Exception as e:
        logger.warning(f"Phase 02 Skipped (unexpected): {e}")
        logger.warning("Renderer will use previously cached statistics if available.")

def run_phase_03():
    """Execute Phase 03: Statistics Engine."""
    try:
        from stats import process_statistics
        logger.info("--- PHASE 03: STATISTICS ENGINE ---")
        process_statistics()
        logger.info("--- PHASE 03 COMPLETED ---")
    except ELSTRIXError as e:
        logger.warning(f"Phase 03 Skipped: {e}")
        logger.warning("Renderer will use previously cached statistics if available.")
    except Exception as e:
        logger.warning(f"Phase 03 Skipped (unexpected): {e}")
        logger.warning("Renderer will use previously cached statistics if available.")

def run_phase_04():
    """Execute Phase 04: Avatar Processing Engine."""
    try:
        from avatar_engine import AvatarPipeline
        pipeline = AvatarPipeline()
        pipeline.run()
    except ELSTRIXError as e:
        logger.error(f"Phase 04 Failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error in Phase 04: {e}", exc_info=True)
        sys.exit(1)

def run_phase_05():
    """Execute Phase 05: SVG Profile Rendering Engine."""
    try:
        from renderer import SVGRenderer
        renderer = SVGRenderer()
        renderer.render()
    except ELSTRIXError as e:
        logger.error(f"Phase 05 Failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error in Phase 05: {e}", exc_info=True)
        sys.exit(1)

def run_phase_06():
    """Execute Phase 06: README Generator Engine."""
    try:
        from readme_engine import ReadmeEngine
        engine = ReadmeEngine()
        engine.run()
    except ELSTRIXError as e:
        logger.error(f"Phase 06 Failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error in Phase 06: {e}", exc_info=True)
        sys.exit(1)

def run_phase_07():
    """Execute Phase 07: Full Automation Engine."""
    try:
        from automation import AutomationEngine
        engine = AutomationEngine()
        engine.run()
    except ELSTRIXError as e:
        logger.error(f"Phase 07 Failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error in Phase 07: {e}", exc_info=True)
        sys.exit(1)

def main():
    initialize()
    logger.info("EL-STRIX foundation is ready.")
    run_phase_02()
    run_phase_03()
    run_phase_04()
    run_phase_05()
    run_phase_06()
    run_phase_07()

if __name__ == "__main__":
    main()
