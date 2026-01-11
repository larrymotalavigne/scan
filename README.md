# Scan Viewer

A full-stack manga scan viewer and scraper with automatic GitHub storage integration.

## Features

- **Automated Scraping**: Scrape manga chapters from supported sites
- **GitHub Storage**: Automatically save and version scans on GitHub
- **Modern UI**: Angular-based responsive manga reader
- **Image Optimization**: Automatic WebP conversion for smaller file sizes
- **Chapter Management**: Track and organize manga chapters
- **Direct CDN Access**: Serve content from GitHub's CDN

## Quick Start

### Backend Setup

1. Install Python dependencies:
```bash
cd back
pip install -r requirements.txt
```

2. Configure GitHub integration in `.env`:
```bash
GITHUB_TOKEN=your_github_token_here
GITHUB_OWNER=atomstudiosfr
GITHUB_REPO=scan
GITHUB_BRANCH=main
```

3. Run the scraper:
```bash
python main.py
```

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd front
npm install
```

2. Run the development server:
```bash
npm start
```

3. Open browser at `http://localhost:4200`

## GitHub Integration

This project automatically saves all scanned content to GitHub, providing:

- Automatic version control and backups
- Free CDN-like hosting via GitHub Pages
- Easy collaboration and deployment
- Direct UI access without separate file server

For detailed setup and usage, see [GITHUB_INTEGRATION.md](GITHUB_INTEGRATION.md)

## Project Structure

```
scan/
├── back/                   # Python backend
│   ├── main.py            # Main scraper
│   ├── github_service.py  # GitHub API integration
│   ├── sync_to_github.py  # Manual sync utility
│   ├── config.json        # Site configuration
│   └── requirements.txt   # Python dependencies
├── front/                 # Angular frontend
│   └── src/
│       └── app/
│           ├── services/  # API services
│           └── pages/     # UI components
└── assets/                # Scanned manga content
    ├── scans.json         # Manga manifest
    └── [manga]/           # Manga directories
        ├── cover.webp     # Cover image
        ├── scans.json     # Chapter metadata
        └── [chapter]/     # Chapter images
```

## Documentation

- [GitHub Integration Guide](GITHUB_INTEGRATION.md) - Complete GitHub setup and usage
- See `back/config.json` for site scraper configuration
- Frontend service: `front/src/app/services/scan.service.ts`

## Technologies

**Backend:**
- Python 3.12+
- httpx (async HTTP client)
- BeautifulSoup4 (HTML parsing)
- Pillow (image processing)
- Pydantic (data validation)

**Frontend:**
- Angular 20.x
- TypeScript
- RxJS
- Angular CDK

## License

MIT
