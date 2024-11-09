import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';

import { timer } from 'rxjs';
import { switchMap } from 'rxjs/operators';

import { RepositoriesService } from '../services/repositories.service';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { OrderToggleComponent } from '../components/order-toggle/order-toggle.component';

@Component({
  selector: 'app-repositories',
  templateUrl: './repositories.component.html',
  styleUrl: './repositories.component.css',
  imports: [CommonModule, RouterModule, OrderToggleComponent],
  standalone: true,
})
export class RepositoriesComponent implements OnInit, OnDestroy {
  subscriptions = new Set<any>();
  repos: any[] = [];
  has_video: any = {};
  video_requested = false;
  reload_request = false;

  @ViewChild('reloaded') reloaded: any;

  order = {
    field: 'timestamp',
    direction: 1,
  };

  constructor(
    public repoService: RepositoriesService,
    public sanitizer: DomSanitizer,
  ) {}

  ngOnInit() {
    this.video_requested = false;
    this.subscriptions.add(
      timer(100, 5 * 60 * 1000)
        .pipe(switchMap(() => this.repoService.getRepositories()))
        .subscribe((data) => this.setRepositories(data as any[])),
    );
  }

  ngOnDestroy() {
    this.subscriptions.forEach((x) => x.unsubscribe());
  }

  setRepositories(data: any[]) {
    this.processReloadRequest();

    this.repos = data
      .map((x) => {
        return {
          ...x,
          codesite: this.sanitizer.bypassSecurityTrustUrl(x.web),
          website: this.sanitizer.bypassSecurityTrustUrl(x.site),
          timestamp: x.date * 1000,
          first: x.start_date * 1000,
        };
      })
      .sort((a, b) => {
        return +b.date - +a.date;
      });

    if (!this.video_requested) {
      this.video_requested = true;

      this.repos.forEach((repo) => {
        this.repoService.hasVideo(repo.name).subscribe(
          (response) => this.setVideoResponse(repo.name, response),
          () => {},
        );
      });
    }
  }

  setVideoResponse(repo: string, response: any) {
    if (response.status === 200) {
      this.has_video = { ...this.has_video, [repo]: true };
    }
  }

  orderBy(field: string) {
    if (field === this.order.field) {
      this.order = { field, direction: -1 * this.order.direction };
    } else {
      this.order = { field, direction: 1 };
    }

    this.repos = this.repos.sort((a, b) => {
      if (field === 'name' || field === 'author') {
        if (this.order.direction === 1) {
          return b[field].localeCompare(a[field]);
        } else {
          return a[field].localeCompare(b[field]);
        }
      }
      return this.order.direction * (b[field] - a[field]);
    });
  }

  refresh() {
    this.reload_request = true;
    this.repoService
      .getRepositories()
      .subscribe((data) => this.setRepositories(data as any[]));
  }

  processReloadRequest() {
    if (!this.reload_request) {
      return;
    }
    this.reload_request = false;

    this.reloaded.nativeElement.classList.remove('d-none');
    setTimeout(() => {
      this.reloaded.nativeElement.classList.add('d-none');
    }, 3000);
  }
}
