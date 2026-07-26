"""Main entry point for EL-STRIX profile and banner updates."""

import sys
import os
from github import GitHubClient
from generator import ProfileGenerator
from renderer import SVGRenderer
from utils import logger


def main():
    logger.info("Starting EL-STRIX generation workflow...")
    username = os.getenv("GITHUB_REPOSITORY_OWNER", "EL-STRIX")

    client = GitHubClient()
    profile = client.get_user_profile(username)
    repos = client.get_user_repos(username)

    generator = ProfileGenerator(username=username)
    data = generator.generate_data(profile, repos)

    renderer = SVGRenderer()
    renderer.render(data)

    logger.info("EL-STRIX generation completed successfully.")


if __name__ == "__main__":
    main()
