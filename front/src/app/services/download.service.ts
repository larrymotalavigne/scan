import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface DownloadJob {
  id: string;
  mangaTitle: string;
  chapters: string[];
  status: 'pending' | 'downloading' | 'completed' | 'failed';
  progress: number;
  currentChapter?: string;
  error?: string;
  startTime?: Date;
  endTime?: Date;
}

@Injectable({
  providedIn: 'root'
})
export class DownloadService {
  private backendUrl = environment.apiUrl;
  private downloadJobs = new BehaviorSubject<DownloadJob[]>([]);
  public downloadJobs$ = this.downloadJobs.asObservable();

  constructor(private http: HttpClient) {
    // Load saved jobs from localStorage
    this.loadJobs();
  }

  /**
   * Download a manga and its chapters
   * @param mangaTitle Manga title
   * @param mangaUrl Source URL for the manga
   * @param chapters Array of chapter URLs to download
   * @returns Observable of download job
   */
  downloadManga(
    mangaTitle: string,
    mangaUrl: string,
    chapters: string[]
  ): Observable<DownloadJob> {
    const job: DownloadJob = {
      id: this.generateJobId(),
      mangaTitle,
      chapters: chapters,
      status: 'pending',
      progress: 0,
      startTime: new Date()
    };

    // Add job to the list
    this.addJob(job);

    // Send download request to backend
    const url = `${this.backendUrl}/download`;
    const body = {
      jobId: job.id,
      mangaTitle,
      mangaUrl,
      chapters
    };

    return this.http.post<any>(url, body).pipe(
      map(response => {
        job.status = 'downloading';
        this.updateJob(job);
        return job;
      }),
      catchError(error => {
        job.status = 'failed';
        job.error = error.message || 'Download failed';
        job.endTime = new Date();
        this.updateJob(job);
        throw error;
      })
    );
  }

  /**
   * Download specific chapters for a manga
   * @param mangaTitle Manga title
   * @param chapterUrls Array of chapter URLs
   * @returns Observable of download job
   */
  downloadChapters(
    mangaTitle: string,
    chapterUrls: string[]
  ): Observable<DownloadJob> {
    const url = `${this.backendUrl}/download-chapters`;
    const body = {
      mangaTitle,
      chapterUrls
    };

    const job: DownloadJob = {
      id: this.generateJobId(),
      mangaTitle,
      chapters: chapterUrls,
      status: 'downloading',
      progress: 0,
      startTime: new Date()
    };

    this.addJob(job);

    return this.http.post<any>(url, body).pipe(
      map(response => {
        job.status = 'completed';
        job.progress = 100;
        job.endTime = new Date();
        this.updateJob(job);
        return job;
      }),
      catchError(error => {
        job.status = 'failed';
        job.error = error.message;
        job.endTime = new Date();
        this.updateJob(job);
        throw error;
      })
    );
  }

  /**
   * Get status of a download job
   * @param jobId Job identifier
   * @returns Observable of job status
   */
  getJobStatus(jobId: string): Observable<DownloadJob> {
    const url = `${this.backendUrl}/download/status/${jobId}`;
    return this.http.get<DownloadJob>(url).pipe(
      map(jobStatus => {
        const jobs = this.downloadJobs.value;
        const index = jobs.findIndex(j => j.id === jobId);
        if (index !== -1) {
          jobs[index] = { ...jobs[index], ...jobStatus };
          this.downloadJobs.next(jobs);
          this.saveJobs();
        }
        return jobStatus;
      })
    );
  }

  /**
   * Get all download jobs
   * @returns Array of download jobs
   */
  getAllJobs(): DownloadJob[] {
    return this.downloadJobs.value;
  }

  /**
   * Clear completed jobs
   */
  clearCompletedJobs(): void {
    const jobs = this.downloadJobs.value.filter(
      job => job.status !== 'completed'
    );
    this.downloadJobs.next(jobs);
    this.saveJobs();
  }

  /**
   * Cancel a download job
   * @param jobId Job identifier
   */
  cancelJob(jobId: string): Observable<any> {
    const url = `${this.backendUrl}/download/cancel/${jobId}`;
    return this.http.post(url, {}).pipe(
      map(() => {
        const jobs = this.downloadJobs.value;
        const job = jobs.find(j => j.id === jobId);
        if (job) {
          job.status = 'failed';
          job.error = 'Cancelled by user';
          job.endTime = new Date();
          this.updateJob(job);
        }
      })
    );
  }

  private generateJobId(): string {
    return `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private addJob(job: DownloadJob): void {
    const jobs = this.downloadJobs.value;
    jobs.push(job);
    this.downloadJobs.next(jobs);
    this.saveJobs();
  }

  private updateJob(updatedJob: DownloadJob): void {
    const jobs = this.downloadJobs.value;
    const index = jobs.findIndex(j => j.id === updatedJob.id);
    if (index !== -1) {
      jobs[index] = updatedJob;
      this.downloadJobs.next(jobs);
      this.saveJobs();
    }
  }

  private saveJobs(): void {
    localStorage.setItem('downloadJobs', JSON.stringify(this.downloadJobs.value));
  }

  private loadJobs(): void {
    const saved = localStorage.getItem('downloadJobs');
    if (saved) {
      try {
        const jobs = JSON.parse(saved);
        this.downloadJobs.next(jobs);
      } catch (e) {
        console.error('Failed to load download jobs:', e);
      }
    }
  }
}
