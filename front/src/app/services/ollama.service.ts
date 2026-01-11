import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface OllamaScanResult {
  title: string;
  author?: string;
  description?: string;
  coverUrl?: string;
  chapters?: OllamaChapter[];
  sourceUrl?: string;
  status?: string;
  genres?: string[];
}

export interface OllamaChapter {
  number: string;
  title?: string;
  url: string;
  releaseDate?: string;
  pages?: string[];
}

export interface SearchResponse {
  results: OllamaScanResult[];
  totalResults?: number;
}

@Injectable({
  providedIn: 'root'
})
export class OllamaService {
  private apiBaseUrl = environment.ollamaApiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Search for manga/scans using the Ollama API
   * @param query Search query string
   * @returns Observable of search results
   */
  searchScans(query: string): Observable<OllamaScanResult[]> {
    const url = `${this.apiBaseUrl}/search`;
    const params = { q: query };

    return this.http.get<any>(url, { params }).pipe(
      map(response => {
        // Handle different response formats
        if (Array.isArray(response)) {
          return response;
        } else if (response.results) {
          return response.results;
        } else if (response.data) {
          return response.data;
        }
        return [];
      }),
      catchError(error => {
        console.error('Search error:', error);
        return throwError(() => new Error('Failed to search scans. Please try again.'));
      })
    );
  }

  /**
   * Get detailed information about a specific scan
   * @param scanId Scan identifier
   * @returns Observable of scan details
   */
  getScanDetails(scanId: string): Observable<OllamaScanResult> {
    const url = `${this.apiBaseUrl}/scan/${scanId}`;
    return this.http.get<OllamaScanResult>(url).pipe(
      catchError(error => {
        console.error('Error fetching scan details:', error);
        return throwError(() => new Error('Failed to fetch scan details.'));
      })
    );
  }

  /**
   * Get chapters for a specific scan
   * @param scanId Scan identifier
   * @returns Observable of chapters
   */
  getChapters(scanId: string): Observable<OllamaChapter[]> {
    const url = `${this.apiBaseUrl}/scan/${scanId}/chapters`;
    return this.http.get<any>(url).pipe(
      map(response => {
        if (Array.isArray(response)) {
          return response;
        } else if (response.chapters) {
          return response.chapters;
        }
        return [];
      }),
      catchError(error => {
        console.error('Error fetching chapters:', error);
        return throwError(() => new Error('Failed to fetch chapters.'));
      })
    );
  }

  /**
   * Get pages for a specific chapter
   * @param chapterUrl Chapter URL or identifier
   * @returns Observable of page URLs
   */
  getChapterPages(chapterUrl: string): Observable<string[]> {
    const url = `${this.apiBaseUrl}/chapter/pages`;
    const params = { url: chapterUrl };

    return this.http.get<any>(url, { params }).pipe(
      map(response => {
        if (Array.isArray(response)) {
          return response;
        } else if (response.pages) {
          return response.pages;
        }
        return [];
      }),
      catchError(error => {
        console.error('Error fetching chapter pages:', error);
        return throwError(() => new Error('Failed to fetch chapter pages.'));
      })
    );
  }

  /**
   * Use Ollama AI to analyze and extract scan information from a URL
   * @param url URL to analyze
   * @returns Observable of extracted scan information
   */
  analyzeScanUrl(url: string): Observable<OllamaScanResult> {
    const apiUrl = `${this.apiBaseUrl}/analyze`;
    const body = { url };

    return this.http.post<OllamaScanResult>(apiUrl, body).pipe(
      catchError(error => {
        console.error('Error analyzing URL:', error);
        return throwError(() => new Error('Failed to analyze URL.'));
      })
    );
  }

  /**
   * Ask Ollama AI a question about finding scans
   * @param prompt User's question or request
   * @returns Observable of AI response with scan recommendations
   */
  askOllama(prompt: string): Observable<any> {
    const url = `${this.apiBaseUrl}/chat`;
    const body = {
      model: 'llama3',
      messages: [
        {
          role: 'system',
          content: 'You are a helpful assistant that helps users find manga and scans. Provide structured information about manga titles, chapters, and where to find them.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      stream: false
    };

    return this.http.post<any>(url, body).pipe(
      catchError(error => {
        console.error('Error asking Ollama:', error);
        return throwError(() => new Error('Failed to get AI response.'));
      })
    );
  }
}
