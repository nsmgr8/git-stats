import { Component, OnInit } from '@angular/core';

import { RepositoriesService } from '../services/repositories.service';

@Component({
    selector: 'app-repositories',
    templateUrl: './repositories.component.html',
    styleUrls: ['./repositories.component.styl']
})
export class RepositoriesComponent implements OnInit {
    subscription;
    repos = [];
    has_video: any = {};

    order = {
        field: 'timestamp',
        direction: 1
    };

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
            this.repoService.hasVideo(repo.name)
                .subscribe(
                    response => this.setVideoResponse(repo.name, response),
                    () => {}
                );
        });
    }

    setVideoResponse(repo, response) {
        if (response.status === 200) {
            this.has_video = {...this.has_video, [repo]: true};
        }
    }

    orderBy(field) {
        if (field === this.order.field) {
            this.order = {field, direction: (-1) * this.order.direction};
        } else {
            this.order = {field, direction: 1};
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
}
