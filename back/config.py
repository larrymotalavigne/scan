import os
from dotenv import load_dotenv
from schema import Config

# Load environment variables
load_dotenv()

# Load site configuration
config = Config.parse_file('config.json')

# GitHub configuration from environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_OWNER = os.getenv('GITHUB_OWNER', 'atomstudiosfr')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'scan')
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'main')
GITHUB_ENABLED = bool(GITHUB_TOKEN)
