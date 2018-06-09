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
    has_video: any = {};

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
                timestamp: x.date * 1000,
                first: x.start_date * 1000
            };
        }).sort((a, b) => {
            return +b.date - +a.date;
        });

        this.repos.forEach(repo => {
            this.repoService.getVideo(repo.name)
                .subscribe(
                    response => this.setVideoResponse(repo.name, response)
                );
        });
    }

    setVideoResponse(repo, response) {
        if (response.status === 200) {
            this.has_video = {...this.has_video, [repo]: true};
        }
    }
}
