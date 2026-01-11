import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { OllamaService, OllamaScanResult, OllamaChapter } from '../services/ollama.service';
import { DownloadService, DownloadJob } from '../services/download.service';

@Component({
  selector: 'app-scan-search',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="scan-search-container">
      <div class="search-header">
        <h1>Search & Download Scans</h1>
        <p>Search for manga using AI-powered search and download chapters directly</p>
      </div>

      <!-- Search Section -->
      <div class="search-section">
        <div class="search-box">
          <input
            type="text"
            [(ngModel)]="searchQuery"
            (keyup.enter)="search()"
            placeholder="Search for manga by title, author, or description..."
            class="search-input"
          />
          <button (click)="search()" [disabled]="isSearching" class="search-button">
            {{ isSearching ? 'Searching...' : 'Search' }}
          </button>
        </div>

        <!-- AI Chat Section -->
        <div class="ai-chat-section">
          <button (click)="toggleAiChat()" class="ai-toggle-button">
            {{ showAiChat ? 'Hide AI Assistant' : 'Ask AI Assistant' }}
          </button>

          <div *ngIf="showAiChat" class="ai-chat-box">
            <textarea
              [(ngModel)]="aiPrompt"
              placeholder="Ask AI to help you find manga... (e.g., 'I want action manga with overpowered main characters')"
              class="ai-input"
              rows="3"
            ></textarea>
            <button (click)="askAi()" [disabled]="isAskingAi" class="ai-button">
              {{ isAskingAi ? 'Asking...' : 'Ask AI' }}
            </button>
            <div *ngIf="aiResponse" class="ai-response">
              <h4>AI Response:</h4>
              <p>{{ aiResponse }}</p>
            </div>
          </div>
        </div>

        <!-- Error Display -->
        <div *ngIf="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
      </div>

      <!-- Search Results -->
      <div class="results-section" *ngIf="searchResults.length > 0">
        <h2>Search Results ({{ searchResults.length }})</h2>

        <div class="results-grid">
          <div *ngFor="let result of searchResults" class="result-card">
            <div class="result-cover" *ngIf="result.coverUrl">
              <img [src]="result.coverUrl" [alt]="result.title" />
            </div>

            <div class="result-info">
              <h3>{{ result.title }}</h3>
              <p class="author" *ngIf="result.author">By {{ result.author }}</p>
              <p class="description">{{ result.description }}</p>

              <div class="meta-info">
                <span *ngIf="result.status" class="status">{{ result.status }}</span>
                <span *ngIf="result.genres" class="genres">{{ result.genres.join(', ') }}</span>
              </div>

              <div class="action-buttons">
                <button (click)="loadChapters(result)" class="btn-primary">
                  View Chapters
                </button>
                <button (click)="downloadAll(result)" class="btn-secondary" *ngIf="result.chapters && result.chapters.length > 0">
                  Download All
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Chapter Selection -->
      <div class="chapter-section" *ngIf="selectedScan">
        <div class="chapter-header">
          <h2>Chapters for {{ selectedScan.title }}</h2>
          <button (click)="closeChapters()" class="close-button">×</button>
        </div>

        <div *ngIf="isLoadingChapters" class="loading">Loading chapters...</div>

        <div *ngIf="!isLoadingChapters && chapters.length > 0" class="chapters-list">
          <div class="chapter-actions">
            <button (click)="selectAllChapters()" class="btn-small">Select All</button>
            <button (click)="deselectAllChapters()" class="btn-small">Deselect All</button>
            <button (click)="downloadSelected()" [disabled]="selectedChapters.length === 0" class="btn-primary">
              Download Selected ({{ selectedChapters.length }})
            </button>
          </div>

          <div class="chapter-item" *ngFor="let chapter of chapters">
            <input
              type="checkbox"
              [checked]="isChapterSelected(chapter)"
              (change)="toggleChapter(chapter)"
              [id]="'chapter-' + chapter.number"
            />
            <label [for]="'chapter-' + chapter.number">
              <span class="chapter-number">Chapter {{ chapter.number }}</span>
              <span class="chapter-title" *ngIf="chapter.title">- {{ chapter.title }}</span>
              <span class="chapter-date" *ngIf="chapter.releaseDate">{{ chapter.releaseDate }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Download Queue -->
      <div class="download-section" *ngIf="downloadJobs.length > 0">
        <h2>Download Queue</h2>

        <div class="download-jobs">
          <div *ngFor="let job of downloadJobs" class="job-card" [class.completed]="job.status === 'completed'" [class.failed]="job.status === 'failed'">
            <div class="job-header">
              <h4>{{ job.mangaTitle }}</h4>
              <span class="job-status">{{ job.status }}</span>
            </div>

            <div class="job-progress" *ngIf="job.status === 'downloading'">
              <div class="progress-bar">
                <div class="progress-fill" [style.width.%]="job.progress"></div>
              </div>
              <span class="progress-text">{{ job.progress }}%</span>
              <p *ngIf="job.currentChapter">Downloading: {{ job.currentChapter }}</p>
            </div>

            <p class="job-info">{{ job.chapters.length }} chapters</p>
            <p class="job-error" *ngIf="job.error">Error: {{ job.error }}</p>

            <div class="job-actions">
              <button *ngIf="job.status === 'downloading'" (click)="cancelJob(job.id)" class="btn-danger">
                Cancel
              </button>
            </div>
          </div>
        </div>

        <button (click)="clearCompleted()" class="btn-secondary">Clear Completed</button>
      </div>
    </div>
  `,
  styles: [`
    .scan-search-container {
      padding: 2rem;
      max-width: 1400px;
      margin: 0 auto;
    }

    .search-header {
      text-align: center;
      margin-bottom: 2rem;
    }

    .search-header h1 {
      font-size: 2.5rem;
      margin-bottom: 0.5rem;
    }

    .search-section {
      margin-bottom: 2rem;
    }

    .search-box {
      display: flex;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .search-input {
      flex: 1;
      padding: 1rem;
      font-size: 1rem;
      border: 2px solid #ddd;
      border-radius: 8px;
    }

    .search-button {
      padding: 1rem 2rem;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 1rem;
      font-weight: 600;
    }

    .search-button:hover:not(:disabled) {
      background: #0056b3;
    }

    .search-button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .ai-chat-section {
      margin-top: 1rem;
    }

    .ai-toggle-button {
      padding: 0.5rem 1rem;
      background: #6c757d;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
    }

    .ai-chat-box {
      margin-top: 1rem;
      padding: 1rem;
      background: #f8f9fa;
      border-radius: 8px;
    }

    .ai-input {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 1rem;
      margin-bottom: 0.5rem;
    }

    .ai-button {
      padding: 0.5rem 1rem;
      background: #28a745;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
    }

    .ai-response {
      margin-top: 1rem;
      padding: 1rem;
      background: white;
      border-radius: 6px;
      border-left: 4px solid #28a745;
    }

    .error-message {
      padding: 1rem;
      background: #f8d7da;
      color: #721c24;
      border-radius: 6px;
      margin-top: 1rem;
    }

    .results-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1.5rem;
    }

    .result-card {
      border: 1px solid #ddd;
      border-radius: 8px;
      overflow: hidden;
      background: white;
      transition: transform 0.2s;
    }

    .result-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .result-cover img {
      width: 100%;
      height: 400px;
      object-fit: cover;
    }

    .result-info {
      padding: 1rem;
    }

    .result-info h3 {
      margin: 0 0 0.5rem 0;
      font-size: 1.25rem;
    }

    .author {
      color: #666;
      font-size: 0.9rem;
      margin: 0 0 0.5rem 0;
    }

    .description {
      font-size: 0.9rem;
      color: #444;
      margin-bottom: 1rem;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .meta-info {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
      flex-wrap: wrap;
    }

    .status, .genres {
      font-size: 0.8rem;
      padding: 0.25rem 0.5rem;
      background: #e9ecef;
      border-radius: 4px;
    }

    .action-buttons {
      display: flex;
      gap: 0.5rem;
    }

    .btn-primary, .btn-secondary, .btn-small, .btn-danger {
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.9rem;
    }

    .btn-primary {
      background: #007bff;
      color: white;
      flex: 1;
    }

    .btn-secondary {
      background: #6c757d;
      color: white;
      flex: 1;
    }

    .btn-danger {
      background: #dc3545;
      color: white;
    }

    .btn-small {
      padding: 0.25rem 0.75rem;
      font-size: 0.85rem;
    }

    .chapter-section {
      position: fixed;
      top: 0;
      right: 0;
      width: 400px;
      height: 100vh;
      background: white;
      box-shadow: -4px 0 12px rgba(0,0,0,0.1);
      overflow-y: auto;
      padding: 1.5rem;
      z-index: 1000;
    }

    .chapter-header {
      display: flex;
      justify-content: space-between;
      align-items: start;
      margin-bottom: 1rem;
    }

    .close-button {
      background: none;
      border: none;
      font-size: 2rem;
      cursor: pointer;
      color: #666;
    }

    .chapter-actions {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
      flex-wrap: wrap;
    }

    .chapters-list {
      margin-top: 1rem;
    }

    .chapter-item {
      display: flex;
      align-items: center;
      padding: 0.75rem;
      border-bottom: 1px solid #eee;
    }

    .chapter-item input[type="checkbox"] {
      margin-right: 0.75rem;
    }

    .chapter-item label {
      flex: 1;
      cursor: pointer;
      display: flex;
      flex-direction: column;
    }

    .chapter-number {
      font-weight: 600;
    }

    .chapter-title {
      color: #666;
      font-size: 0.9rem;
    }

    .chapter-date {
      font-size: 0.8rem;
      color: #999;
    }

    .download-section {
      margin-top: 2rem;
      padding: 1.5rem;
      background: #f8f9fa;
      border-radius: 8px;
    }

    .download-jobs {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .job-card {
      padding: 1rem;
      background: white;
      border-radius: 6px;
      border-left: 4px solid #007bff;
    }

    .job-card.completed {
      border-left-color: #28a745;
    }

    .job-card.failed {
      border-left-color: #dc3545;
    }

    .job-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
    }

    .job-status {
      font-size: 0.85rem;
      padding: 0.25rem 0.5rem;
      background: #e9ecef;
      border-radius: 4px;
      text-transform: uppercase;
    }

    .job-progress {
      margin: 0.5rem 0;
    }

    .progress-bar {
      width: 100%;
      height: 8px;
      background: #e9ecef;
      border-radius: 4px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: #007bff;
      transition: width 0.3s;
    }

    .progress-text {
      font-size: 0.9rem;
      color: #666;
    }

    .job-error {
      color: #dc3545;
      font-size: 0.9rem;
    }

    .loading {
      text-align: center;
      padding: 2rem;
      color: #666;
    }
  `]
})
export class ScanSearchComponent implements OnInit {
  searchQuery: string = '';
  searchResults: OllamaScanResult[] = [];
  isSearching: boolean = false;
  errorMessage: string = '';

  showAiChat: boolean = false;
  aiPrompt: string = '';
  aiResponse: string = '';
  isAskingAi: boolean = false;

  selectedScan: OllamaScanResult | null = null;
  chapters: OllamaChapter[] = [];
  selectedChapters: OllamaChapter[] = [];
  isLoadingChapters: boolean = false;

  downloadJobs: DownloadJob[] = [];

  constructor(
    private ollamaService: OllamaService,
    private downloadService: DownloadService
  ) {}

  ngOnInit(): void {
    // Subscribe to download jobs
    this.downloadService.downloadJobs$.subscribe(jobs => {
      this.downloadJobs = jobs;
    });
  }

  search(): void {
    if (!this.searchQuery.trim()) {
      return;
    }

    this.isSearching = true;
    this.errorMessage = '';
    this.searchResults = [];

    this.ollamaService.searchScans(this.searchQuery).subscribe({
      next: (results) => {
        this.searchResults = results;
        this.isSearching = false;
        if (results.length === 0) {
          this.errorMessage = 'No results found. Try a different search term.';
        }
      },
      error: (error) => {
        this.errorMessage = error.message || 'Failed to search. Please try again.';
        this.isSearching = false;
      }
    });
  }

  toggleAiChat(): void {
    this.showAiChat = !this.showAiChat;
    if (!this.showAiChat) {
      this.aiResponse = '';
    }
  }

  askAi(): void {
    if (!this.aiPrompt.trim()) {
      return;
    }

    this.isAskingAi = true;
    this.aiResponse = '';

    this.ollamaService.askOllama(this.aiPrompt).subscribe({
      next: (response) => {
        this.aiResponse = response.message?.content || response.response || JSON.stringify(response);
        this.isAskingAi = false;
      },
      error: (error) => {
        this.aiResponse = 'Failed to get AI response. Please try again.';
        this.isAskingAi = false;
      }
    });
  }

  loadChapters(scan: OllamaScanResult): void {
    this.selectedScan = scan;
    this.selectedChapters = [];

    if (scan.chapters && scan.chapters.length > 0) {
      this.chapters = scan.chapters;
      this.isLoadingChapters = false;
    } else {
      this.isLoadingChapters = true;
      // Assuming scan has an ID or we can derive it from the title
      const scanId = scan.title.toLowerCase().replace(/\s+/g, '-');
      this.ollamaService.getChapters(scanId).subscribe({
        next: (chapters) => {
          this.chapters = chapters;
          this.isLoadingChapters = false;
        },
        error: (error) => {
          this.errorMessage = 'Failed to load chapters';
          this.isLoadingChapters = false;
        }
      });
    }
  }

  closeChapters(): void {
    this.selectedScan = null;
    this.chapters = [];
    this.selectedChapters = [];
  }

  toggleChapter(chapter: OllamaChapter): void {
    const index = this.selectedChapters.findIndex(c => c.number === chapter.number);
    if (index > -1) {
      this.selectedChapters.splice(index, 1);
    } else {
      this.selectedChapters.push(chapter);
    }
  }

  isChapterSelected(chapter: OllamaChapter): boolean {
    return this.selectedChapters.some(c => c.number === chapter.number);
  }

  selectAllChapters(): void {
    this.selectedChapters = [...this.chapters];
  }

  deselectAllChapters(): void {
    this.selectedChapters = [];
  }

  downloadSelected(): void {
    if (!this.selectedScan || this.selectedChapters.length === 0) {
      return;
    }

    const chapterUrls = this.selectedChapters.map(c => c.url);
    this.downloadService.downloadChapters(
      this.selectedScan.title,
      chapterUrls
    ).subscribe({
      next: (job) => {
        console.log('Download started:', job);
        this.closeChapters();
      },
      error: (error) => {
        this.errorMessage = 'Failed to start download: ' + error.message;
      }
    });
  }

  downloadAll(scan: OllamaScanResult): void {
    if (!scan.chapters || scan.chapters.length === 0) {
      this.errorMessage = 'No chapters available to download';
      return;
    }

    const chapterUrls = scan.chapters.map(c => c.url);
    this.downloadService.downloadManga(
      scan.title,
      scan.sourceUrl || '',
      chapterUrls
    ).subscribe({
      next: (job) => {
        console.log('Download all started:', job);
      },
      error: (error) => {
        this.errorMessage = 'Failed to start download: ' + error.message;
      }
    });
  }

  cancelJob(jobId: string): void {
    this.downloadService.cancelJob(jobId).subscribe();
  }

  clearCompleted(): void {
    this.downloadService.clearCompletedJobs();
  }
}
