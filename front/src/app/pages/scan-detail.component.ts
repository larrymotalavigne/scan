import { Component, OnInit } from '@angular/core';

import { ActivatedRoute, Router } from '@angular/router';
import { ScanService } from '../services/scan.service';
import { CardModule } from 'primeng/card';

@Component({
    selector: 'app-scan-detail',
    imports: [CardModule],
    template: `
    @if (manga) {
      <div class="container">
        <div class="detail-section">
          <div class="cover">
            <img [src]="manga.cover" alt="{{manga.title}} cover">
          </div>
          <div class="details">
            <h1>{{manga.title}}</h1>
            <p><strong>Author:</strong> {{manga.author}}</p>
            <p><strong>Description:</strong> {{manga.description}}</p>
          </div>
        </div>
        @if (chapters) {
          <div class="chapters-section">
            <h2>Chapters</h2>
            <div class="chapters-container">
              @for (chapter of chapters; track chapter) {
                <div class="chapter-card" (click)="viewChapter(chapter)">
                  <p-card>
                    <ng-template pTemplate="title">
                      {{chapter.title}}
                    </ng-template>
                  </p-card>
                </div>
              }
            </div>
          </div>
        }
      </div>
    }
    `,
    styles: [`
    .container {
      padding: 20px;
    }
    .detail-section {
      display: flex;
      flex-wrap: wrap;
      margin-bottom: 20px;
    }
    .cover {
      flex: 1;
      min-width: 200px;
      max-width: 300px;
      margin-right: 20px;
    }
    .cover img {
      width: 100%;
      height: auto;
    }
    .details {
      flex: 2;
      min-width: 200px;
    }
    .chapters-section {
      width: 100%;
    }
    .chapters-container {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    .chapter-card {
      flex: 1 1 calc(33.333% - 10px);
      min-width: 150px;
      cursor: pointer;
    }
    @media (max-width: 768px) {
      .detail-section {
        flex-direction: column;
        align-items: center;
      }
      .cover {
        margin-right: 0;
        margin-bottom: 20px;
      }
      .chapters-container {
        flex-direction: column;
      }
      .chapter-card {
        flex: 1 1 100%;
      }
    }
  `]
})
export class ScanDetailComponent implements OnInit {
  manga: any;
  chapters: any[];

  constructor(private route: ActivatedRoute, private scanService: ScanService, private router: Router) {}

  ngOnInit(): void {
    const mangaTitle = this.route.snapshot.paramMap.get('title');
    if (mangaTitle) {
      this.scanService.getMangaDetails(mangaTitle).subscribe(mangaData => {
        this.manga = mangaData;
        this.scanService.getChapterDetails(mangaTitle).subscribe(chapterData => {
          this.chapters = chapterData;
        });
      });
    }
  }

  viewChapter(chapter: any): void {
    this.router.navigate(['/viewer', this.manga.title, chapter.title]);
  }
}
