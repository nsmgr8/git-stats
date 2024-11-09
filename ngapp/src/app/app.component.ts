import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterModule, RouterOutlet } from '@angular/router';
import { RepositoriesService } from './services/repositories.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule, RouterModule],
  templateUrl: './app.component.html',
})
export class AppComponent implements OnInit {
  last_updated = 0;

  constructor(public repoService: RepositoriesService) {}

  ngOnInit() {
    this.repoService
      .get('last_update.json')
      .subscribe((data: any) => (this.last_updated = data.last_updated * 1000));
  }
}
