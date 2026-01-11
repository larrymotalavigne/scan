import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home.component';
import { ScanDetailComponent } from './pages/scan-detail.component';
import { ChapterViewerComponent } from './pages/chapter-viewer.component';
import { ScanSearchComponent } from './pages/scan-search.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'search', component: ScanSearchComponent },
  { path: 'viewer/:title', component: ScanDetailComponent },
  { path: 'viewer/:manga/:chapter', component: ChapterViewerComponent },
  { path: '**', redirectTo: '', pathMatch: 'full' }  // Wildcard route to handle undefined routes
];
