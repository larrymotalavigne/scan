# Search & Download Feature

This document explains the new AI-powered search and download interface for finding and downloading manga scans.

## Overview

The Search & Download feature allows users to:

1. **Search for manga** using the Ollama AI API
2. **Browse search results** with cover images and details
3. **View available chapters** for each manga
4. **Select and download chapters** directly to the GitHub repository
5. **Track download progress** in real-time
6. **Use AI assistant** to get recommendations

## Architecture

### Frontend Components

#### 1. Ollama Service (`front/src/app/services/ollama.service.ts`)
- Interfaces with the Ollama AI API at `ollama.atomstudios.fr`
- Provides methods for:
  - Searching manga by title, author, or description
  - Getting manga details and chapters
  - AI-powered chat for recommendations
  - Analyzing manga URLs

#### 2. Download Service (`front/src/app/services/download.service.ts`)
- Manages download jobs and queue
- Tracks download progress
- Persists download history in localStorage
- Communicates with backend API for actual downloads

#### 3. Search Component (`front/src/app/pages/scan-search.component.ts`)
- Main UI for search and download interface
- Features:
  - Search input with real-time results
  - AI chat assistant
  - Chapter selection sidebar
  - Download queue management
  - Progress tracking

### Backend API

#### API Server (`back/api_server.py`)
FastAPI server providing endpoints for download management:

**Endpoints:**
- `POST /api/download` - Start downloading a manga with all chapters
- `POST /api/download-chapters` - Download specific chapters
- `GET /api/download/status/{job_id}` - Check download job status
- `POST /api/download/cancel/{job_id}` - Cancel a download job
- `GET /api/jobs` - List all download jobs
- `DELETE /api/jobs/completed` - Clear completed jobs

**Features:**
- Background task processing
- Progress tracking
- Automatic GitHub integration
- Chapter metadata management

## Setup

### Prerequisites

1. **Ollama API Access**
   - API endpoint: `https://ollama.atomstudios.fr/api`
   - Required for search functionality
   - Contact administrator for access credentials if needed

2. **Backend Dependencies**
   ```bash
   cd back
   pip install -r requirements.txt
   ```

3. **Frontend Dependencies**
   ```bash
   cd front
   npm install
   ```

### Configuration

#### 1. Environment Variables

Update `.env` file (if Ollama API requires authentication):
```bash
# Ollama API (if authentication is needed)
OLLAMA_API_KEY=your_api_key_here
```

#### 2. Frontend Configuration

The frontend is pre-configured in `environment.ts`:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',
  ollamaApiUrl: 'https://ollama.atomstudios.fr/api'
};
```

For production (`environment.prod.ts`):
```typescript
export const environment = {
  production: true,
  apiUrl: '/api',
  ollamaApiUrl: 'https://ollama.atomstudios.fr/api'
};
```

### Running the Application

#### 1. Start the Backend API Server

```bash
cd back
python api_server.py
```

The API server will start on `http://localhost:8000`

#### 2. Start the Frontend Development Server

```bash
cd front
npm start
```

The frontend will be available at `http://localhost:4200`

#### 3. Navigate to Search Page

Click "Search & Download" in the navigation menu or visit `http://localhost:4200/search`

## Usage Guide

### Basic Search

1. **Enter search query**
   - Type manga title, author name, or keywords
   - Press Enter or click "Search" button

2. **Browse results**
   - View manga cover images
   - Read descriptions and metadata
   - See available chapters

3. **Download options**
   - Click "View Chapters" to select specific chapters
   - Click "Download All" to download entire manga

### Using AI Assistant

1. **Open AI Chat**
   - Click "Ask AI Assistant" button
   - Chat interface expands

2. **Ask for recommendations**
   - Example: "I want action manga with overpowered main characters"
   - Example: "Find me romance manga similar to Horimiya"
   - Example: "What are the top-rated isekai manga?"

3. **Get AI response**
   - AI provides recommendations
   - Use suggestions to search for specific titles

### Chapter Selection

1. **Open chapter list**
   - Click "View Chapters" on any manga result
   - Sidebar opens with all available chapters

2. **Select chapters**
   - Check individual chapters
   - Use "Select All" / "Deselect All" buttons

3. **Download selected**
   - Click "Download Selected (X)" button
   - Download job starts immediately

### Download Management

1. **Monitor progress**
   - Download queue appears at bottom of page
   - Real-time progress bars
   - Current chapter information

2. **Job statuses**
   - **Pending**: Queued for download
   - **Downloading**: Currently in progress
   - **Completed**: Successfully finished
   - **Failed**: Error occurred

3. **Cancel downloads**
   - Click "Cancel" on active download
   - Job marked as cancelled

4. **Clear completed**
   - Click "Clear Completed" button
   - Removes finished jobs from queue

## How It Works

### Search Flow

1. **User enters search query**
2. **Frontend calls Ollama API** (`/api/search`)
3. **Ollama AI processes query** and returns results
4. **Results displayed** with covers, descriptions, metadata
5. **User selects manga** to view chapters

### Download Flow

1. **User selects chapters** to download
2. **Frontend creates download job** with unique ID
3. **Request sent to backend API** (`POST /api/download-chapters`)
4. **Backend starts background task**:
   - Fetches chapter pages
   - Downloads images
   - Converts to WebP format
   - Updates JSON metadata
   - Uploads to GitHub (if enabled)
5. **Progress updates** sent to frontend
6. **Job marked complete** when finished

### Integration with GitHub

When GitHub integration is enabled:
- Downloaded chapters automatically pushed to repository
- Assets folder structure maintained
- Scans.json files updated
- Frontend can immediately access new scans

## API Reference

### Ollama API Endpoints

**Search Scans**
```
GET /api/search?q={query}
Response: Array of scan results
```

**Get Scan Details**
```
GET /api/scan/{scanId}
Response: Detailed scan information
```

**Get Chapters**
```
GET /api/scan/{scanId}/chapters
Response: Array of chapters
```

**AI Chat**
```
POST /api/chat
Body: {
  model: 'llama3',
  messages: [...],
  stream: false
}
Response: AI-generated response
```

### Backend API Endpoints

**Download Manga**
```
POST /api/download
Body: {
  jobId: string,
  mangaTitle: string,
  mangaUrl: string,
  chapters: string[]
}
Response: {
  message: "Download started",
  jobId: string
}
```

**Download Chapters**
```
POST /api/download-chapters
Body: {
  mangaTitle: string,
  chapterUrls: string[]
}
Response: {
  message: "Download started",
  jobId: string
}
```

**Get Job Status**
```
GET /api/download/status/{jobId}
Response: {
  id: string,
  mangaTitle: string,
  status: string,
  progress: number,
  currentChapter: string,
  chapters: string[],
  error?: string
}
```

**Cancel Job**
```
POST /api/download/cancel/{jobId}
Response: {
  message: "Download cancelled"
}
```

## Troubleshooting

### Search Not Working

**Problem**: Search returns no results or errors

**Solutions**:
1. Check Ollama API is accessible: `curl https://ollama.atomstudios.fr/api`
2. Verify API endpoint in `environment.ts`
3. Check browser console for CORS errors
4. Ensure API authentication (if required)

### Downloads Failing

**Problem**: Downloads start but fail immediately

**Solutions**:
1. Check backend API server is running
2. Verify backend can access scan websites
3. Check file permissions on assets directory
4. Review backend console logs for errors
5. Ensure GitHub token is valid (if GitHub integration enabled)

### AI Chat Not Responding

**Problem**: AI assistant doesn't return responses

**Solutions**:
1. Verify Ollama API endpoint
2. Check API supports `/chat` endpoint
3. Ensure model name is correct ('llama3')
4. Review network requests in browser DevTools

### Download Progress Not Updating

**Problem**: Progress bar stuck at 0%

**Solutions**:
1. Check backend task is running (console logs)
2. Verify job ID is correct
3. Poll status endpoint manually: `GET /api/download/status/{jobId}`
4. Check for JavaScript errors in console

## Advanced Configuration

### Custom Ollama API

To use a different Ollama API or self-hosted instance:

1. Update `environment.ts`:
```typescript
export const environment = {
  ollamaApiUrl: 'http://your-ollama-server:11434/api'
};
```

2. Update CORS settings if needed in backend

### Custom Search Endpoints

Modify `ollama.service.ts` to use different endpoints:

```typescript
searchScans(query: string): Observable<OllamaScanResult[]> {
  const url = `${this.apiBaseUrl}/your-custom-search`;
  // ... implementation
}
```

### Batch Download Limits

Adjust batch size in `api_server.py`:

```python
# Process chapters in batches of 5 (instead of all at once)
for i in range(0, len(chapter_urls), 5):
    batch = chapter_urls[i:i + 5]
    # ... process batch
```

## Security Considerations

1. **API Authentication**
   - Add authentication headers if Ollama API requires it
   - Store API keys in environment variables, not in code

2. **Rate Limiting**
   - Implement rate limiting on backend API
   - Prevent abuse of download endpoints

3. **Input Validation**
   - Validate all URLs before downloading
   - Sanitize manga titles for file paths

4. **CORS Configuration**
   - In production, restrict CORS to specific origins
   - Don't use wildcard (`*`) in production

## Performance Tips

1. **Search Optimization**
   - Debounce search input (300ms delay)
   - Cache recent search results
   - Implement pagination for large result sets

2. **Download Optimization**
   - Limit concurrent downloads (max 3)
   - Queue additional downloads
   - Resume failed downloads

3. **UI Performance**
   - Virtual scrolling for long chapter lists
   - Lazy load images in search results
   - Optimize re-renders with change detection

## Future Enhancements

Planned improvements:
- [ ] Resume interrupted downloads
- [ ] Schedule downloads for later
- [ ] Download history and analytics
- [ ] Export/import download queues
- [ ] Advanced search filters (genre, year, status)
- [ ] Batch operations (download multiple manga)
- [ ] Notification system for completed downloads
- [ ] Integration with MAL/AniList for metadata

## Support

For issues or questions:
- Check troubleshooting section above
- Review backend logs: `tail -f api_server.log`
- Review browser console for frontend errors
- Test Ollama API directly with curl/Postman
- Check GitHub integration status

## Related Documentation

- [GitHub Integration Guide](GITHUB_INTEGRATION.md) - Setup GitHub storage
- [Main README](README.md) - General project information
- Backend API: `back/api_server.py`
- Frontend Component: `front/src/app/pages/scan-search.component.ts`
