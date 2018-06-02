import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { RepositoriesService } from '../../services/repositories.service';

@Component({
    selector: 'app-authors',
    templateUrl: './authors.component.html',
    styleUrls: ['./authors.component.styl']
})
export class AuthorsComponent implements OnInit {
    subscription;
    activity;
    authors;
    repo;
    order = {
        field: 'commits',
        direction: 1
    };

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
        this.subscription = this.repoService.getRepoActivity(name)
            .subscribe(
                data => this.setRepoActivity(data)
            );
    }

    setRepoActivity(data) {
        this.activity = data;
        const authors = Object.keys(data.by_authors);
        this.authors = authors.map(a => {
            let {commits, insertions, deletions} = data.by_authors[a].yearly;
            commits = Object.values(commits).reduce((acc: number, val: number) => acc + val, 0);
            if (insertions) {
                insertions = Object.values(insertions).reduce((acc: number, val: number) => acc + val, 0);
            }
            if (deletions) {
                deletions = Object.values(deletions).reduce((acc: number, val: number) => acc + val, 0);
            }
            return {
                author: a,
                commits,
                insertions,
                deletions,
                ...data.authors_age[a]
            };
        }).sort((a, b) => {
            return b.commits - a.commits;
        });
    }

    toggleOrder(field) {
        if (this.order.field === field) {
            this.order.direction = -1 * this.order.direction;
        } else {
            this.order = {field, direction: 1};
        }
        this.authors = this.authors.sort((a, b) => {
            return this.order.direction * (b[field] - a[field]);
        });
    }
}
