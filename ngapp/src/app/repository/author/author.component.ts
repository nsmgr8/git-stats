import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { RepositoriesService } from '../../services/repositories.service';

@Component({
    selector: 'app-author',
    templateUrl: './author.component.html',
    styleUrls: ['./author.component.styl']
})
export class AuthorComponent implements OnInit {
    subscription;
    author_data;
    author;
    repo;

    charts;
    active_days = 0;

    hours = Array.from({length: 24}, (_, i) => i);

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

    getRepo({name, author}: any) {
        this.repo = name;
        this.author = author;
        this.subscription = this.repoService.getRepoActivity(name)
            .subscribe(
                data => this.setRepoActivity(data)
            );
    }

    setRepoActivity(data) {
        this.author_data = data.by_authors[this.author];
        const author_daily = data.by_authors[this.author].daily;
        const years = {};
        const daily = Object.keys(author_daily.commits);
        let max_commits = 0;

        daily.forEach(day => {
            const [y] = day.split('-');
            this.active_days += 1;

            const commits = author_daily.commits[day];
            const insertions = author_daily.insertions[day];
            const deletions = author_daily.deletions[day];

            if (commits > max_commits) {
                max_commits = commits;
            }

            const row = {
                day,
                commits,
                insertions,
                deletions
            };

            if (years[y]) {
                years[y].push(row);
            } else {
                years[y] = [row];
            }
        });

        this.setHeatmap(years, max_commits);
    }

    setHeatmap(years, max_commits) {
        this.charts = Object.keys(years).sort((a, b) => {
            return +b - +a;
        }).map((year, yi) => ({
            tooltip: {
                position: 'top',
                formatter: value => {
                    const data = years[year][value.dataIndex];
                    return `
                        <table>
                            <thead>
                                <tr>
                                    <th colspan="2">
                                        ${data.day}
                                    </th>
                                </tr>
                            </thead>

                            <tbody>
                                <tr>
                                    <th>Commits</th>
                                    <td class="text-right">
                                        ${data.commits}
                                    </td>
                                </tr>

                                <tr>
                                    <th>Lines Added</th>
                                    <td class="text-right">
                                        ${data.insertions}
                                    </td>
                                </tr>

                                <tr>
                                    <th>Lines Removed</th>
                                    <td class="text-right">
                                        ${data.deletions}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    `;
                }
            },

            visualMap: {
                min: 0,
                max: max_commits,
                show: yi === 0,
                orient: 'horizontal',
                left: 'center',
                top: 'top'
            },

            calendar: [{
                range: year,
                cellSize: ['auto', 20]
            }],

            series: [{
                type: 'heatmap',
                coordinateSystem: 'calendar',
                calendarIndex: 0,
                data: years[year].map(x => [x.day, x.commits])
            }]
        }));
    }
}
