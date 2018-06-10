import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { RepositoriesService } from '../../services/repositories.service';

@Component({
    selector: 'app-age',
    templateUrl: './age.component.html',
    styleUrls: ['./age.component.styl']
})
export class AgeComponent implements OnInit {
    repo;
    subscription;
    active_days = 0;

    years;
    max_values = {
        commits: 0,
        insertions: 0,
        deletions: 0
    };
    charts = [];
    chart_type = 'commits';

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
        const years = {};
        const daily = Object.keys(data.by_time.daily.commits);
        const max_values = {
            commits: 0,
            insertions: 0,
            deletions: 0
        };

        daily.forEach(day => {
            const [y] = day.split('-');
            this.active_days += 1;

            const commits = data.by_time.daily.commits[day];
            const insertions = data.by_time.daily.insertions[day];
            const deletions = data.by_time.daily.deletions[day];

            if (commits > max_values.commits) {
                max_values.commits = commits;
            }

            if (insertions && insertions > max_values.insertions) {
                max_values.insertions = insertions;
            }

            if (deletions && deletions > max_values.deletions) {
                max_values.deletions = deletions;
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

        this.years = years;
        this.max_values = max_values;
        this.setHeatmap(this.chart_type);
    }

    setHeatmap(chart_type) {
        this.chart_type = chart_type;
        const years = this.years;
        const max_value = this.max_values[chart_type];

        this.charts = Object.keys(years).sort((a, b) => {
            return +b - +a;
        }).map(year => ({
            tooltip: {
                position: 'top',
                confine: true,
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
                max: max_value,
                inRange: {
                    color: ['#eee', '#7bc96f', '#196127']
                }
            },

            calendar: [{
                range: year,
                cellSize: ['auto', 20]
            }],

            series: [{
                type: 'heatmap',
                coordinateSystem: 'calendar',
                calendarIndex: 0,
                data: years[year].map(x => [x.day, x[chart_type]])
            }]
        }));
    }
}
