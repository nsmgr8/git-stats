import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';

import { RepositoriesService } from '../../services/repositories.service';
import { CommonModule } from '@angular/common';
import { NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-repository',
  templateUrl: './repository.component.html',
  styleUrl: './repository.component.css',
  imports: [RouterModule, CommonModule, NgbTooltipModule],
  standalone: true,
})
export class RepositoryComponent implements OnInit, OnDestroy {
  subscriptions = new Set<any>();
  summary: any;
  repo: any = {};

  constructor(
    public repoService: RepositoriesService,
    public sanitizer: DomSanitizer,
    public route: ActivatedRoute,
  ) {}

  ngOnInit() {
    this.route.params.subscribe((params) => this.getRepo(params));
  }

  ngOnDestroy() {
    this.subscriptions.forEach((x) => x.unsubscribe());
  }

  getRepo({ name }: any) {
    this.subscriptions.add(
      this.repoService
        .getRepoSummary(name)
        .subscribe((data) => this.setRepoSummary(data as any[])),
    );
    this.subscriptions.add(
      this.repoService
        .getRepositories()
        .subscribe((data) => this.setRepoMeta(data as any[], name)),
    );
  }

  setRepoMeta(data: any[], name: string) {
    const repo = data.find((x) => x.name === name);
    this.repo = {
      ...repo,
      codesite: this.sanitizer.bypassSecurityTrustUrl(repo.web),
      website: this.sanitizer.bypassSecurityTrustUrl(repo.site),
    };
  }

  setRepoSummary(data: any[]) {
    this.summary = data.sort((a, b) => {
      return a.key.localeCompare(b.key);
    });
  }
}
