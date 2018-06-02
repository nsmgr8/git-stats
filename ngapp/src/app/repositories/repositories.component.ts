import { Component, OnInit } from '@angular/core';

import { RepositoriesService } from '../services/repositories.service';

@Component({
    selector: 'app-repositories',
    templateUrl: './repositories.component.html',
    styleUrls: ['./repositories.component.styl']
})
export class RepositoriesComponent implements OnInit {
    subscription;
    repos;

    constructor(
        public repoService: RepositoriesService
    ) {
    }

    ngOnInit() {
        this.subscription = this.repoService.getRepositories()
            .subscribe(
                data => this.setRepositories(data)
            );
    }

    setRepositories(data) {
        this.repos = data.map(x => {
            return {
                ...x,
                timestamp: x.date * 1000
            };
        }).sort((a, b) => {
            return +b.date - +a.date;
        });
    }
}
