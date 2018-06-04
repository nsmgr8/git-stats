import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { RepositoriesService } from '../../services/repositories.service';

@Component({
    selector: 'app-tags',
    templateUrl: './tags.component.html',
    styleUrls: ['./tags.component.styl']
})
export class TagsComponent implements OnInit {
    repo;
    tags;

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
        this.repoService.getTags(name)
            .subscribe(
                data => this.setTags(data)
            );
    }

    setTags(data) {
        this.tags = data.map(x => {
            const authors = x.authors && x.authors.sort((a, b) => b.commits - a.commits) || [];
            const commits = authors.reduce((acc, val) => acc + val.commits, 0);
            return {
                tag: x.tag,
                timestamp: x.timestamp * 1000,
                authors,
                commits
            };
        });
    }
}
