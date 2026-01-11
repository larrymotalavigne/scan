"""
Manual sync utility to upload all existing assets to GitHub.

This script allows you to manually sync all local scan files to GitHub
without running the full scraper. Useful for:
- Initial setup
- Recovering from sync failures
- Manually uploading edited content
"""

import asyncio
import os
import sys
from pathlib import Path

from config import GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH, GITHUB_ENABLED, config
from github_service import GitHubService


async def sync_all_assets():
    """Sync all assets to GitHub."""
    if not GITHUB_ENABLED:
        print("❌ GitHub integration is not enabled!")
        print("Please set GITHUB_TOKEN in your .env file")
        return False

    print(f"🚀 Starting GitHub sync...")
    print(f"   Repository: {GITHUB_OWNER}/{GITHUB_REPO}")
    print(f"   Branch: {GITHUB_BRANCH}")
    print()

    # Initialize GitHub service
    github_service = GitHubService(
        token=GITHUB_TOKEN,
        owner=GITHUB_OWNER,
        repo=GITHUB_REPO,
        branch=GITHUB_BRANCH
    )

    # Get assets directory from config
    if not config.sites:
        print("❌ No sites configured in config.json")
        return False

    site = config.sites[0]
    assets_dir = site.downloads_dir

    # Check if assets directory exists
    if not os.path.exists(assets_dir):
        print(f"❌ Assets directory not found: {assets_dir}")
        return False

    # Get directory size and file count
    total_files = 0
    total_size = 0
    for root, dirs, files in os.walk(assets_dir):
        total_files += len(files)
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)

    print(f"📊 Found {total_files} files ({total_size / (1024*1024):.2f} MB)")
    print()

    # Confirm with user
    response = input("Do you want to proceed with the sync? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Sync cancelled.")
        return False

    print()
    print("📤 Starting upload to GitHub...")
    print("This may take a while for large repositories...")
    print()

    # Sync all assets
    success = await github_service.sync_all_assets(assets_dir)

    if success:
        print()
        print("✅ Sync completed successfully!")
        print(f"🔗 View your repository at: https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}")
        return True
    else:
        print()
        print("⚠️  Sync completed with some errors. Check the output above.")
        return False


async def sync_specific_manga(manga_title: str):
    """Sync a specific manga to GitHub."""
    if not GITHUB_ENABLED:
        print("❌ GitHub integration is not enabled!")
        print("Please set GITHUB_TOKEN in your .env file")
        return False

    print(f"🚀 Syncing manga: {manga_title}")

    # Initialize GitHub service
    github_service = GitHubService(
        token=GITHUB_TOKEN,
        owner=GITHUB_OWNER,
        repo=GITHUB_REPO,
        branch=GITHUB_BRANCH
    )

    # Get manga directory
    site = config.sites[0]
    manga_dir = os.path.join(site.downloads_dir, manga_title)

    if not os.path.exists(manga_dir):
        print(f"❌ Manga directory not found: {manga_dir}")
        return False

    # Upload manga
    success = await github_service.upload_manga(manga_dir, manga_title)

    # Upload root scans.json
    root_json_path = os.path.join(site.downloads_dir, 'scans.json')
    if os.path.exists(root_json_path):
        await github_service.upload_root_json(root_json_path)

    if success:
        print(f"✅ Successfully synced {manga_title}")
        return True
    else:
        print(f"⚠️  Failed to sync {manga_title}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Sync specific manga
        manga_title = ' '.join(sys.argv[1:])
        asyncio.run(sync_specific_manga(manga_title))
    else:
        # Sync all assets
        asyncio.run(sync_all_assets())


if __name__ == "__main__":
    main()
