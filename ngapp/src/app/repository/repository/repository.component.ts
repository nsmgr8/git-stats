import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { RepositoriesService } from '../../services/repositories.service';

@Component({
    selector: 'app-repository',
    templateUrl: './repository.component.html',
    styleUrls: ['./repository.component.styl']
})
export class RepositoryComponent implements OnInit {
    subscription;
    summary;
    repo;

    constructor(
        public repoService: RepositoriesService,
        public route: ActivatedRoute
    ) {
    }

    ngOnInit() {
        this.route.params.subscribe(
            params => this.getRepo(params)
        );
    }

    getRepo({name}: any) {
        this.repo = name;
        this.subscription = this.repoService.getRepoSummary(name)
            .subscribe(
                data => this.setRepoSummary(data)
            );
    }

    setRepoSummary(data) {
        this.summary = data.sort((a, b) => {
            return a.key.localeCompare(b.key);
        });
    }
}
