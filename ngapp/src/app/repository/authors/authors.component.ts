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
            let {commit, insertions, deletions} = data.by_authors[a].yearly;
            commit = Object.values(commit).reduce((acc: number, val: number) => acc + val, 0);
            if (insertions) {
                insertions = Object.values(insertions).reduce((acc: number, val: number) => acc + val, 0);
            }
            if (deletions) {
                deletions = Object.values(deletions).reduce((acc: number, val: number) => acc + val, 0);
            }
            return {
                author: a,
                commit,
                insertions,
                deletions,
                ...data.authors_age[a]
            };
        }).sort((a, b) => {
            return b.commit - a.commit;
        });
    }

}
