import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { formatDate } from '@angular/common';

import { RepositoriesService } from '../../services/repositories.service';

@Component({
    selector: 'app-branches',
    templateUrl: './branches.component.html',
    styleUrls: ['./branches.component.styl']
})
export class BranchesComponent implements OnInit {
    repo;
    branches;

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
        this.repoService.getBranches(name)
            .subscribe(
                data => this.setBranches(data)
            );
    }

    setBranches(data) {
        const branches = {};
        data.sort((a, b) => {
            return b.timestamp - a.timestamp;
        }).forEach(x => {
            x.timestamp = x.timestamp * 1000;
            const month = formatDate(x.timestamp, 'MMMM y', 'en-GB');
            if (branches[month]) {
                branches[month].push(x);
            } else {
                branches[month] = [x];
            }
        });

        this.branches = Object.keys(branches).map(x => ({month: x, branches: branches[x]}));
    }
}
