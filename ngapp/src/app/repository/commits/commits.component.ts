import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { RepositoriesService } from '../../services/repositories.service';

@Component({
    selector: 'app-commits',
    templateUrl: './commits.component.html',
    styleUrls: ['./commits.component.styl']
})
export class CommitsComponent implements OnInit {
    subscription;
    repo;
    activity;
    hour_of_week;
    weekdays_total;
    total_commit;

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
        this.setHourOfWeek(data);
    }

    setHourOfWeek(data) {
        let max = 0;
        Object.values(data.hour_of_week).forEach(x => Object.values(x).forEach(y => {
            if (y > max) {
                max = y;
            }
        }));

        const hours = Array.from({length: 24}, (_, i) => i);
        const weeks = Array.from({length: 7}, (_, i) => i);

        this.hour_of_week = hours.map(hour => {
            return weeks.map(week => {
                if (data.hour_of_week[week]) {
                    return {
                        value: data.hour_of_week[week][hour],
                        color: makeColor(data.hour_of_week[week][hour], max)
                    };
                }
                return {};
            });
        });

        this.weekdays_total = weeks.map(week => {
            if (data.hour_of_week[week]) {
                return Object.values(data.hour_of_week[week]).reduce((acc: number, val: number) => acc + val, 0);
            }
        });

        this.total_commit = this.weekdays_total.reduce((acc, val) => val ? acc + val : acc, 0);
    }

}

const makeColor = function(value, max) {
    if (!value) {
        return;
    }

    const half = Math.round(max / 2);
    let r = 255, g = 255;
    const b = 0;

    if (value < half) {
        g = Math.round(value * (255 / half));
    } else {
        r = 255 - Math.round((value - half) * (255 / half));
    }

    return `rgba(${r},${g},${b},0.3)`;
};