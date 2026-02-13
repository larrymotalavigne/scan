import { Component, OnInit } from '@angular/core';

import { Router } from '@angular/router';
import { CarouselModule } from 'primeng/carousel';
import { ButtonModule } from 'primeng/button';
import { ScanService } from '../services/scan.service';

@Component({
    selector: 'app-home',
    imports: [CarouselModule, ButtonModule],
    template: `
    <div class="home">
      <h1>Available Scans/Manga</h1>
      <p-carousel [value]="scans" numVisible="3" numScroll="3" [responsiveOptions]="responsiveOptions">
        <ng-template pTemplate="item" let-scan>
          <div class="manga-item">
            <img [src]="scan.cover" alt="{{scan.title}} cover" class="manga-cover">
            <div class="manga-details">
              <h2>{{scan.title}}</h2>
              <p>{{scan.author}}</p>
              <button pButton type="button" label="View" (click)="viewScan(scan)"></button>
            </div>
          </div>
        </ng-template>
      </p-carousel>
    </div>
  `,
    styles: [`
    .manga-cover {
      width: 100%;
      height: auto;
    }
    .manga-item {
      padding: 1rem;
      text-align: center;
    }
    .manga-details {
      margin-top: 1rem;
    }
  `]
})
export class HomeComponent implements OnInit {
  scans: any[];
  responsiveOptions: any[];

  constructor(private scanService: ScanService, private router: Router) {
    this.responsiveOptions = [
      {
        breakpoint: '1024px',
        numVisible: 3,
        numScroll: 3
      },
      {
        breakpoint: '768px',
        numVisible: 2,
        numScroll: 2
      },
      {
        breakpoint: '560px',
        numVisible: 1,
        numScroll: 1
      }
    ];
  }

  ngOnInit(): void {
    this.scanService.getScans().subscribe(data => this.scans = data);
  }

  viewScan(scan): void {
    this.scanService.selectScan(scan);
    this.router.navigate(['/viewer', scan.title]);
  }
}
