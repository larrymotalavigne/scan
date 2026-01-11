# GitHub Integration for Scan Storage

This document explains how the scan storage system works with GitHub integration.

## Overview

The scan project has been refactored to automatically save all scanned manga content to GitHub. This provides:

- **Automatic backups**: All scans are automatically committed to GitHub
- **Version control**: Track changes to scans over time
- **Easy deployment**: Frontend can directly access scans from GitHub
- **CDN-like delivery**: GitHub serves images via raw.githubusercontent.com

## Architecture

### Backend (Python)
1. **Scrapes manga sites** for new chapters and images
2. **Saves files locally** to `../assets/` directory
3. **Automatically uploads to GitHub** using GitHub API
4. **Updates JSON metadata** for manga and chapter listings

### Frontend (Angular)
- **Reads from GitHub** via `https://raw.githubusercontent.com/atomstudiosfr/scan/main/assets/`
- **Displays manga list** from `assets/scans.json`
- **Shows chapter details** from `assets/{manga_title}/scans.json`
- **Loads images** directly from GitHub raw URLs

### Storage Structure
```
assets/
├── scans.json                          # Root manifest of all manga
├── Manga Title 1/
│   ├── cover.webp                      # Manga cover image
│   ├── scans.json                      # Chapter metadata
│   ├── 1/                              # Chapter 1
│   │   ├── 1.webp
│   │   ├── 2.webp
│   │   └── ...
│   ├── 2/                              # Chapter 2
│   │   └── ...
│   └── ...
└── Manga Title 2/
    └── ...
```

## Setup

### 1. Create GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "Scan Backend"
4. Select the following scopes:
   - `repo` (Full control of private repositories)
5. Click "Generate token"
6. **Copy the token** - you won't see it again!

### 2. Configure Environment Variables

Edit the `.env` file in the project root:

```bash
# GitHub Integration
GITHUB_TOKEN=ghp_your_token_here
GITHUB_OWNER=atomstudiosfr
GITHUB_REPO=scan
GITHUB_BRANCH=main
```

**Important**:
- Replace `ghp_your_token_here` with your actual GitHub token
- Update `GITHUB_OWNER` and `GITHUB_REPO` to match your repository
- Never commit the `.env` file with your token to version control!

### 3. Install Dependencies

```bash
cd back
pip install -r requirements.txt
```

## Usage

### Running the Scraper

The scraper will automatically upload to GitHub when configured:

```bash
cd back
python main.py
```

Output will show:
```
✓ GitHub integration enabled - will push to atomstudiosfr/scan
Scraping manga from site...
✓ Uploaded assets/Manga Title/cover.webp
✓ Uploaded assets/Manga Title/1/1.webp
...
📤 Uploading manga 'Manga Title' to GitHub...
✓ Uploaded 150 files for Manga Title
```

### Manual Sync to GitHub

To manually sync existing assets to GitHub:

```bash
cd back
python sync_to_github.py
```

This will:
1. Show you the number of files to upload
2. Ask for confirmation
3. Upload all files to GitHub
4. Show progress and results

To sync a specific manga:
```bash
python sync_to_github.py "Manga Title"
```

### Disabling GitHub Integration

If you want to run the scraper without uploading to GitHub, simply remove or comment out the `GITHUB_TOKEN` in your `.env` file:

```bash
# GITHUB_TOKEN=ghp_your_token_here
```

The scraper will run normally but only save files locally.

## How It Works

### Automatic Upload Flow

1. **Scraper runs** and downloads manga chapters
2. **Files saved locally** to `../assets/manga_title/chapter_number/`
3. **After each manga completes**:
   - Cover image uploaded to GitHub
   - All chapter images uploaded to GitHub
   - Chapter metadata (`scans.json`) uploaded to GitHub
4. **After all mangas complete**:
   - Root manifest (`scans.json`) uploaded to GitHub

### GitHub API Integration

The `github_service.py` module handles all GitHub operations:

- **File upload**: Uses GitHub Contents API
- **Update detection**: Checks if file exists and gets SHA
- **Batch operations**: Efficiently uploads multiple files
- **Error handling**: Continues on errors, reports failures

### Frontend Access

The Angular frontend is pre-configured to read from GitHub:

- Base URL: `https://raw.githubusercontent.com/atomstudiosfr/scan/main/assets/`
- Manga list: `{baseUrl}scans.json`
- Manga cover: `{baseUrl}{manga_title}/cover.webp`
- Chapter metadata: `{baseUrl}{manga_title}/scans.json`
- Chapter images: `{baseUrl}{manga_title}/{chapter_number}/{page_number}.webp`

No frontend changes are needed - it automatically works with GitHub storage!

## Troubleshooting

### "GitHub integration disabled" message

**Solution**: Check that `GITHUB_TOKEN` is set in your `.env` file.

### "Failed to upload" errors

**Possible causes**:
1. Invalid GitHub token
2. Insufficient permissions (need `repo` scope)
3. Repository doesn't exist
4. Network issues
5. File too large (GitHub has a 100MB file limit)

**Solutions**:
- Verify token has `repo` scope
- Check repository exists at `github.com/{owner}/{repo}`
- Check network connection
- For large files, consider using Git LFS

### Rate limiting

GitHub API has rate limits:
- **5,000 requests/hour** for authenticated requests
- Each file upload counts as one request

For large manga libraries, the sync may take time due to rate limits.

## Security Best Practices

1. **Never commit** `.env` file with tokens
2. **Use environment-specific** tokens (dev vs prod)
3. **Rotate tokens** periodically
4. **Use fine-grained tokens** when available (currently using classic tokens for compatibility)
5. **Limit token scope** to only what's needed (`repo` scope)

## Benefits of GitHub Storage

✅ **Automatic backups**: All content versioned and backed up
✅ **Free hosting**: GitHub provides free hosting for public repos
✅ **CDN delivery**: Fast global access via GitHub's CDN
✅ **Version control**: Track all changes to scans
✅ **Collaboration**: Multiple scrapers can push to same repo
✅ **Accessibility**: UI can access scans without separate file server

## Architecture Diagram

```
┌─────────────────┐
│  Manga Sites    │
└────────┬────────┘
         │ scrape
         ▼
┌─────────────────┐
│  Backend        │
│  (Python)       │
│  - Scraper      │
│  - Image Save   │
│  - JSON Update  │
└────────┬────────┘
         │ upload
         ▼
┌─────────────────┐
│  GitHub Repo    │
│  assets/        │
│  - scans.json   │
│  - manga/       │
│    - chapters/  │
└────────┬────────┘
         │ fetch
         ▼
┌─────────────────┐
│  Frontend       │
│  (Angular)      │
│  - UI Display   │
│  - Image Load   │
└─────────────────┘
```

## Migration from Local Storage

If you have existing local assets that need to be uploaded to GitHub:

1. Ensure all assets are in the `assets/` directory
2. Configure GitHub credentials in `.env`
3. Run the manual sync utility:
   ```bash
   python sync_to_github.py
   ```
4. Verify files are uploaded by checking your GitHub repository

## Future Enhancements

Potential improvements for the GitHub integration:

- [ ] Use Git LFS for large image files
- [ ] Implement batch commits (multiple files in one commit)
- [ ] Add retry logic with exponential backoff
- [ ] Support for multiple branches (dev/staging/prod)
- [ ] Webhook notifications on successful uploads
- [ ] GitHub Actions for automated deployments
- [ ] Incremental sync (only upload changed files)

## Support

For issues or questions:
- Check the troubleshooting section above
- Review GitHub API documentation: https://docs.github.com/en/rest
- Check GitHub token permissions
- Verify repository access
