import asyncio
import os

from config import config, GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH, GITHUB_ENABLED
from parsers import parse_manga_list_page, parse_manga_page, parse_manga_details, parse_chapter_page
from update_json import update_root_scans_json, update_manga_scans_json
from utils import fetch_page, save_images, save_image, extract_chapter_number, clean_chapters
from github_service import GitHubService


async def get_cleaned_images(chapter_dir):
    # List all files in the directory after cleaning
    return [os.path.join(chapter_dir, f) for f in os.listdir(chapter_dir) if os.path.isfile(os.path.join(chapter_dir, f))]


async def process_chapter(site, manga_dir, chapter_url):
    chapter_number = extract_chapter_number(chapter_url)
    if chapter_number is None:
        return
    chapter_dir = os.path.join(manga_dir, str(chapter_number))
    if site.ignore_existing_chapter and os.path.exists(chapter_dir):
        print(f"Skipping chapter: {chapter_number} of manga: {manga_dir}, already exists")
        return
    chapter_page_html = await fetch_page(chapter_url)
    if chapter_page_html:
        images = await parse_chapter_page(chapter_page_html, site.selectors)
        webp_images = await save_images(images, chapter_dir, site.overwrite)
        # clean_directory(chapter_dir)
        # cleaned_images = await get_cleaned_images(chapter_dir)
        update_manga_scans_json(site, manga_dir, str(chapter_number), cleaned_images)


async def process_manga(site, manga_url, manga_title, github_service=None):
    manga_dir = os.path.join(site.downloads_dir, manga_title)
    if site.ignore_existing_manga and os.path.exists(manga_dir):
        print(f"Skipping manga: {manga_title}, already exists")
        return
    manga_page_html = await fetch_page(manga_url)
    if manga_page_html:
        description, author, cover_url = await parse_manga_details(manga_page_html, site.selectors)
        if cover_url:
            cover_path = os.path.join(manga_dir, 'cover.webp')
            await save_image(cover_url, cover_path, site.overwrite)
        chapters = await parse_manga_page(manga_page_html, site.selectors)
        chapters = clean_chapters(chapters)
        chapters = [ch for ch in chapters if extract_chapter_number(ch) is not None]
        chapters.sort(key=extract_chapter_number)

        # Process chapters in batches of 10
        for i in range(0, len(chapters), 10):
            batch = chapters[i:i + 10]
            tasks = [process_chapter(site, manga_dir, ch) for ch in batch]
            try:
                await asyncio.gather(*tasks)
            except Exception as e:
                print(f"Error processing batch {i // 10 + 1}: {e}")

        # Update root scans.json after processing all chapters
        update_root_scans_json(site, manga_title, description, author, cover_url)

        # Upload manga files to GitHub if enabled
        if github_service and os.path.exists(manga_dir):
            await github_service.upload_manga(manga_dir, manga_title)


async def main():
    # Initialize GitHub service if enabled
    github_service = None
    if GITHUB_ENABLED:
        github_service = GitHubService(
            token=GITHUB_TOKEN,
            owner=GITHUB_OWNER,
            repo=GITHUB_REPO,
            branch=GITHUB_BRANCH
        )
        print(f"✓ GitHub integration enabled - will push to {GITHUB_OWNER}/{GITHUB_REPO}")
    else:
        print("⚠ GitHub integration disabled - files will only be saved locally")

    for site in config.sites:
        main_page_html = await fetch_page(site.site_url)
        if main_page_html:
            manga_links = parse_manga_list_page(main_page_html, site.selectors)
            for manga_url, manga_title in manga_links:
                try:
                    await process_manga(site, manga_url, manga_title, github_service)  # Ensure mangas are processed sequentially
                except Exception as e:
                    print(f"Error processing manga {manga_title}: {e}")

            # Upload root scans.json to GitHub after processing all mangas
            if github_service:
                root_json_path = os.path.join(site.downloads_dir, 'scans.json')
                if os.path.exists(root_json_path):
                    await github_service.upload_root_json(root_json_path)


if __name__ == "__main__":
    asyncio.run(main())
