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
        console.log(data);
        const repo_names = Object.keys(data);
        this.repos = repo_names.map(x => {
            return {
                name: x,
                ...data[x],
                timestamp: data[x].Date * 1000
            };
        }).sort((a, b) => {
            return +b.Date - +a.Date;
        });
    }
}
