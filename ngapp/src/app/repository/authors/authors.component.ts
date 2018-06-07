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
    authors;
    repo;
    order = {
        field: 'commits',
        direction: 1
    };
    period_order = {
        field: 'commits',
        direction: 1
    };

    order_title = {
        commits: 'Commits',
        insertions: 'Lines Added',
        deletions: 'Lines Removed'
    };

    author_of_the_periods;

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
        this.setAuthors(data);
        this.author_of_the_periods = [
            'weekly', 'monthly', 'yearly'
        ].map(period => ({
            type: period,
            value: this.setAuthorOfThePeriod(data, period)
        }));
    }

    setAuthors(data) {
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

    togglePeriodOrder(field) {
        if (this.period_order.field === field) {
            this.period_order.direction = -1 * this.period_order.direction;
        } else {
            this.period_order = {field, direction: 1};
        }

        this.author_of_the_periods = this.author_of_the_periods.map(x => {
            return {
                ...x,
                value: x.value.map(y => {
                    return {
                        ...y,
                        data: y.data.sort((a, b) => {
                            return this.period_order.direction * (b[field] - a[field]);
                        })
                    };
                })
            };
        });
    }

    setAuthorOfThePeriod(data, period) {
        const authors = Object.keys(data.by_authors);
        const rows = {};
        authors.forEach(a => {
            const {commits, insertions, deletions} = data.by_authors[a][period];
            Object.keys(commits).forEach(key => {
                const row = {
                    author: a,
                    commits: commits[key],
                    insertions: insertions && insertions[key],
                    deletions: deletions && deletions[key]
                };

                if (rows[key]) {
                    rows[key].push(row);
                } else {
                    rows[key] = [row];
                }
            });
        });

        return Object.keys(rows)
            .sort((a, b) => {
                return b.localeCompare(a);
            }).map(x => {
                return {
                    period: x,
                    data: rows[x].sort((a, b) => b.commits - a.commits)
                };
            });
    }
}
