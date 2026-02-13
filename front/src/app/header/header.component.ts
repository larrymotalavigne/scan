import { Component, OnInit } from '@angular/core';

import { MenubarModule } from 'primeng/menubar';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { MenuItem } from 'primeng/api';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ScanService } from '../services/scan.service';
import { ThemeService } from '../services/theme.service';

@Component({
    selector: 'app-header',
    imports: [MenubarModule, InputTextModule, ButtonModule, AutoCompleteModule, FormsModule],
    template: `
    <p-menubar [model]="items">
      <ng-template pTemplate="start">
        <img src="assets/logo.webp" routerLink="/" height="40" alt="logo">
      </ng-template>
      <ng-template pTemplate="end">
        <p-autoComplete
          [(ngModel)]="selectedManga"
          [suggestions]="filteredMangas"
          (completeMethod)="onSearch($event)"
          field="title"
          [dropdown]="true"
          placeholder="Search manga..."
          (onSelect)="navigateToManga(selectedManga)">
          <ng-template let-manga pTemplate="item">
            <div class="p-d-flex p-ai-center">
              <img [src]="manga.cover" alt="{{manga.title}} cover" width="40" class="p-mr-2">
              <div>{{manga.title}}</div>
            </div>
          </ng-template>
        </p-autoComplete>
        <button pButton icon="pi pi-moon" class="p-button-rounded p-button-outlined" (click)="toggleDarkMode()"></button>
      </ng-template>
    </p-menubar>
  `,
    styles: [`
    :host {
      display: block;
    }
    p-menubar {
      background: var(--surface-a);
      color: var(--text-color);
    }
  `]
})
export class HeaderComponent implements OnInit {
  items: MenuItem[];
  searchQuery: string = '';
  currentTheme: string = 'light';
  selectedManga: any;
  filteredMangas: any[];

  constructor(private scanService: ScanService, private themeService: ThemeService, private router: Router) {}

  ngOnInit() {
    this.items = [
      { label: 'Home', icon: 'pi pi-fw pi-home', routerLink: ['/'] },
      { label: 'Viewer', icon: 'pi pi-fw pi-eye', routerLink: ['/viewer'] }
    ];
    this.applyTheme();
  }

  onSearch(event: any) {
    this.scanService.searchScans(event.query).subscribe((results) => {
      this.filteredMangas = results;
    });
  }

  toggleDarkMode() {
    this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
    this.themeService.switchTheme(this.currentTheme);
    localStorage.setItem('theme', this.currentTheme);
  }

  applyTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    this.currentTheme = theme;
    this.themeService.switchTheme(theme);
  }

  navigateToManga(manga: any) {
    this.router.navigate(['/viewer', manga.title]);
  }
}
