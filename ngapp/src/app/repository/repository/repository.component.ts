import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';

import { RepositoriesService } from '../../services/repositories.service';

@Component({
    selector: 'app-repository',
    templateUrl: './repository.component.html',
    styleUrls: ['./repository.component.styl']
})
export class RepositoryComponent implements OnInit, OnDestroy {
    subscriptions = new Set<any>();
    summary;
    repo: any = {};

    constructor(
        public repoService: RepositoriesService,
        public sanitizer: DomSanitizer,
        public route: ActivatedRoute
    ) {
    }

    ngOnInit() {
        this.route.params.subscribe(
            params => this.getRepo(params)
        );
    }

    ngOnDestroy() {
        this.subscriptions.forEach(x => x.unsubscribe());
    }

    getRepo({name}: any) {
        this.subscriptions.add(
            this.repoService.getRepoSummary(name).subscribe(
                data => this.setRepoSummary(data)
            )
        );
        this.subscriptions.add(
            this.repoService.getRepositories().subscribe(
                data => this.setRepoMeta(data, name)
            )
        );
    }

    setRepoMeta(data, name) {
        const repo = data.find(x => x.name === name);
        this.repo = {
            ...repo,
            codesite: this.sanitizer.bypassSecurityTrustUrl(repo.web),
            website: this.sanitizer.bypassSecurityTrustUrl(repo.site),
        };
    }

    setRepoSummary(data) {
        this.summary = data.sort((a, b) => {
            return a.key.localeCompare(b.key);
        });
    }
}
