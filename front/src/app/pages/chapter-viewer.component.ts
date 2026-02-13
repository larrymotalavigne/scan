import { Component, OnInit } from '@angular/core';

import { ActivatedRoute } from '@angular/router';
import { ScanService } from '../services/scan.service';

@Component({
    selector: 'app-chapter-viewer',
    imports: [],
    template: `
    @if (pages) {
      <div class="chapter-viewer">
        <h1>{{mangaTitle}} - {{chapterTitle}}</h1>
        <div class="pages">
          @for (page of pages; track page) {
            <img [src]="page" alt="Page">
          }
        </div>
      </div>
    }
    `,
    styles: [`
    .chapter-viewer {
      padding: 20px;
    }
    .pages {
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .pages img {
      width: 100%;
      max-width: 800px;
      margin-bottom: 10px;
    }
  `]
})
export class ChapterViewerComponent implements OnInit {
  mangaTitle: string;
  chapterTitle: string;
  pages: string[];

  constructor(private route: ActivatedRoute, private scanService: ScanService) {}

  ngOnInit(): void {
    this.mangaTitle = this.route.snapshot.paramMap.get('manga');
    this.chapterTitle = this.route.snapshot.paramMap.get('chapter');
    this.scanService.getChapterDetails(this.mangaTitle).subscribe(data => {
      const chapter = data.find(ch => ch.title === this.chapterTitle);
      if (chapter) {
        this.pages = chapter.pages;
      }
    });
  }
}
