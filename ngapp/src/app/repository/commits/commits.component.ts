import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { RepositoriesService } from '../../services/repositories.service';
import { CommonModule } from '@angular/common';
import { PeriodPipe } from '../../pipes/period.pipe';

@Component({
  selector: 'app-commits',
  templateUrl: './commits.component.html',
  standalone: true,
  imports: [CommonModule, PeriodPipe],
})
export class CommitsComponent implements OnInit {
  subscription: any;
  videoSubscription: any;

  repo: string = '';
  activity: any;
  hour_of_week: any;
  weekdays_total?: number[];
  total_commit: any;

  commitsByPeriod: any;
  videoUrl = '';

  constructor(
    public repoService: RepositoriesService,
    public route: ActivatedRoute,
  ) {}

  ngOnInit() {
    this.route.params.subscribe((params) => this.getRepo(params));
  }

  getRepo(params: any) {
    const name = params.name;
    this.repo = name;
    this.subscription = this.repoService
      .getRepoActivity(name)
      .subscribe((data) => this.setRepoActivity(data));
    this.videoSubscription = this.repoService
      .hasVideo(name)
      .subscribe((response) => this.videoResponse(response));
  }

  videoResponse(response: any) {
    if (response.status === 200) {
      this.videoUrl = this.repoService.videoUrl(this.repo);
    }
  }

  setRepoActivity(data: any) {
    this.activity = data;
    this.setHourOfWeek(data);
    this.commitsByPeriod = ['yearly', 'monthly'].map((period) => ({
      type: period,
      value: this.setCommitPeriods(data, period),
    }));
  }

  setHourOfWeek(
    data: Record<'hour_of_week', Record<number, Record<number, number>>>,
  ) {
    let max = 0;
    Object.values(data.hour_of_week).forEach((x) =>
      Object.values(x).forEach((y) => {
        if (y > max) {
          max = y;
        }
      }),
    );

    const hours = Array.from({ length: 24 }, (_, i) => i);
    const weeks = Array.from({ length: 7 }, (_, i) => i);

    this.hour_of_week = hours.map((hour) => {
      return weeks.map((week) => {
        if (data.hour_of_week[week]) {
          return {
            value: data.hour_of_week[week][hour],
            color: makeColor(data.hour_of_week[week][hour], max),
          };
        }
        return {};
      });
    });

    this.weekdays_total = weeks.map((week) => {
      if (data.hour_of_week[week]) {
        return (Object.values(data.hour_of_week[week]) as number[]).reduce(
          (acc: number, val: number) => acc + val,
          0,
        );
      }
      return 0;
    });

    this.total_commit = this.weekdays_total.reduce(
      (acc, val) => (val ? acc + val : acc),
      0,
    );
  }

  setCommitPeriods(data: any, period: any) {
    const { commits, insertions, deletions } = data.by_time[period];
    return Object.keys(commits)
      .sort((a, b) => {
        return b.localeCompare(a);
      })
      .map((key) => {
        return {
          period: key,
          commits: commits[key],
          insertions: insertions && insertions[key],
          deletions: deletions && deletions[key],
        };
      });
  }
}

export const makeColor = function (value: number, max: number) {
  if (!value) {
    return;
  }

  const half = Math.round(max / 2);
  let r = 255,
    g = 255;
  const b = 0;

  if (value < half) {
    g = Math.round(value * (255 / half));
  } else {
    r = 255 - Math.round((value - half) * (255 / half));
  }

  return `rgba(${r},${g},${b},0.3)`;
};
