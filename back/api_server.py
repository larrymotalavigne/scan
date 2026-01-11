"""
FastAPI server for handling scan download requests from the frontend.

This server provides endpoints for:
- Downloading manga chapters from URLs
- Checking download status
- Managing download jobs
"""

import asyncio
import os
from typing import List, Dict, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn

from config import config, GITHUB_ENABLED
from parsers import parse_chapter_page, parse_manga_details, parse_manga_page
from utils import fetch_page, save_images, save_image, extract_chapter_number, clean_chapters
from update_json import update_root_scans_json, update_manga_scans_json
from github_service import GitHubService

# Initialize FastAPI app
app = FastAPI(
    title="Scan Download API",
    description="API for downloading and managing manga scans",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Download job storage (in production, use Redis or database)
download_jobs: Dict[str, dict] = {}


class DownloadRequest(BaseModel):
    jobId: str
    mangaTitle: str
    mangaUrl: str
    chapters: List[str]


class ChapterDownloadRequest(BaseModel):
    mangaTitle: str
    chapterUrls: List[str]


class DownloadStatus(BaseModel):
    id: str
    mangaTitle: str
    status: str
    progress: float
    currentChapter: Optional[str] = None
    error: Optional[str] = None
    chapters: List[str]


async def download_chapter_task(
    manga_title: str,
    chapter_url: str,
    site_config,
    github_service: Optional[GitHubService] = None
):
    """Download a single chapter."""
    try:
        manga_dir = os.path.join(site_config.downloads_dir, manga_title)
        chapter_number = extract_chapter_number(chapter_url)

        if chapter_number is None:
            print(f"Could not extract chapter number from {chapter_url}")
            return False

        chapter_dir = os.path.join(manga_dir, str(chapter_number))

        if site_config.ignore_existing_chapter and os.path.exists(chapter_dir):
            print(f"Skipping chapter: {chapter_number}, already exists")
            return True

        # Fetch chapter page
        chapter_page_html = await fetch_page(chapter_url)
        if not chapter_page_html:
            print(f"Failed to fetch chapter page: {chapter_url}")
            return False

        # Parse images
        images = await parse_chapter_page(chapter_page_html, site_config.selectors)
        if not images:
            print(f"No images found in chapter: {chapter_url}")
            return False

        # Download images
        webp_images = await save_images(images, chapter_dir, site_config.overwrite)

        # Update JSON metadata
        update_manga_scans_json(site_config, manga_dir, str(chapter_number), webp_images)

        # Upload to GitHub if enabled
        if github_service:
            await github_service.upload_manga(manga_dir, manga_title)

        return True

    except Exception as e:
        print(f"Error downloading chapter {chapter_url}: {e}")
        return False


async def download_manga_task(
    job_id: str,
    manga_title: str,
    manga_url: str,
    chapter_urls: List[str],
    github_service: Optional[GitHubService] = None
):
    """Background task to download manga chapters."""
    site_config = config.sites[0]  # Use first site config

    try:
        # Update job status
        download_jobs[job_id]['status'] = 'downloading'
        download_jobs[job_id]['progress'] = 0

        manga_dir = os.path.join(site_config.downloads_dir, manga_title)

        # Fetch manga details if URL provided
        if manga_url:
            manga_page_html = await fetch_page(manga_url)
            if manga_page_html:
                description, author, cover_url = await parse_manga_details(
                    manga_page_html,
                    site_config.selectors
                )

                # Save cover image
                if cover_url:
                    cover_path = os.path.join(manga_dir, 'cover.webp')
                    await save_image(cover_url, cover_path, site_config.overwrite)

                # Update root scans.json
                update_root_scans_json(site_config, manga_title, description, author, cover_url)

        # Download chapters
        total_chapters = len(chapter_urls)
        for i, chapter_url in enumerate(chapter_urls):
            download_jobs[job_id]['currentChapter'] = f"Chapter {i+1}/{total_chapters}"
            download_jobs[job_id]['progress'] = (i / total_chapters) * 100

            success = await download_chapter_task(
                manga_title,
                chapter_url,
                site_config,
                github_service
            )

            if not success:
                print(f"Failed to download chapter: {chapter_url}")

        # Upload root JSON to GitHub
        if github_service:
            root_json_path = os.path.join(site_config.downloads_dir, 'scans.json')
            if os.path.exists(root_json_path):
                await github_service.upload_root_json(root_json_path)

        # Mark as completed
        download_jobs[job_id]['status'] = 'completed'
        download_jobs[job_id]['progress'] = 100
        download_jobs[job_id]['currentChapter'] = None

    except Exception as e:
        download_jobs[job_id]['status'] = 'failed'
        download_jobs[job_id]['error'] = str(e)
        print(f"Error in download task: {e}")


@app.post("/api/download")
async def download_manga(request: DownloadRequest, background_tasks: BackgroundTasks):
    """
    Start downloading a manga and its chapters.
    """
    # Create job entry
    download_jobs[request.jobId] = {
        'id': request.jobId,
        'mangaTitle': request.mangaTitle,
        'status': 'pending',
        'progress': 0,
        'chapters': request.chapters,
        'currentChapter': None,
        'error': None
    }

    # Initialize GitHub service if enabled
    github_service = None
    if GITHUB_ENABLED:
        from config import GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH
        github_service = GitHubService(
            token=GITHUB_TOKEN,
            owner=GITHUB_OWNER,
            repo=GITHUB_REPO,
            branch=GITHUB_BRANCH
        )

    # Start download task in background
    background_tasks.add_task(
        download_manga_task,
        request.jobId,
        request.mangaTitle,
        request.mangaUrl,
        request.chapters,
        github_service
    )

    return {"message": "Download started", "jobId": request.jobId}


@app.post("/api/download-chapters")
async def download_chapters(request: ChapterDownloadRequest, background_tasks: BackgroundTasks):
    """
    Download specific chapters for a manga.
    """
    import uuid
    job_id = f"job_{uuid.uuid4().hex[:8]}"

    # Create job entry
    download_jobs[job_id] = {
        'id': job_id,
        'mangaTitle': request.mangaTitle,
        'status': 'pending',
        'progress': 0,
        'chapters': request.chapterUrls,
        'currentChapter': None,
        'error': None
    }

    # Initialize GitHub service if enabled
    github_service = None
    if GITHUB_ENABLED:
        from config import GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH
        github_service = GitHubService(
            token=GITHUB_TOKEN,
            owner=GITHUB_OWNER,
            repo=GITHUB_REPO,
            branch=GITHUB_BRANCH
        )

    # Start download task in background
    background_tasks.add_task(
        download_manga_task,
        job_id,
        request.mangaTitle,
        "",  # No manga URL for chapter-only downloads
        request.chapterUrls,
        github_service
    )

    return {"message": "Download started", "jobId": job_id}


@app.get("/api/download/status/{job_id}")
async def get_download_status(job_id: str):
    """
    Get the status of a download job.
    """
    if job_id not in download_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return download_jobs[job_id]


@app.post("/api/download/cancel/{job_id}")
async def cancel_download(job_id: str):
    """
    Cancel a download job.
    """
    if job_id not in download_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    download_jobs[job_id]['status'] = 'cancelled'
    download_jobs[job_id]['error'] = 'Cancelled by user'

    return {"message": "Download cancelled"}


@app.get("/api/jobs")
async def get_all_jobs():
    """
    Get all download jobs.
    """
    return list(download_jobs.values())


@app.delete("/api/jobs/completed")
async def clear_completed_jobs():
    """
    Clear all completed jobs.
    """
    global download_jobs
    download_jobs = {
        k: v for k, v in download_jobs.items()
        if v['status'] not in ['completed', 'cancelled']
    }
    return {"message": "Completed jobs cleared"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Scan Download API",
        "version": "1.0.0",
        "endpoints": {
            "download": "/api/download",
            "download_chapters": "/api/download-chapters",
            "status": "/api/download/status/{job_id}",
            "jobs": "/api/jobs"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
