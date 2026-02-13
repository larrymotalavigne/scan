import { Component } from '@angular/core';

import { RouterModule } from '@angular/router';
import { HeaderComponent } from './header/header.component';
import { FooterComponent } from './footer/footer.component';

@Component({
    selector: 'app-root',
    imports: [RouterModule, HeaderComponent, FooterComponent],
    template: `
    <app-header></app-header>
    <main class="main-content">
      <router-outlet></router-outlet>
    </main>
    <app-footer></app-footer>
  `,
    styles: [`
    .main-content {
      padding-top: 60px; /* Adjust based on your header height */
      padding-bottom: 60px; /* Adjust based on your footer height */
    }
  `]
})
export class AppComponent {
  title = 'scan-viewer';
}
