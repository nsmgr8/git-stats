import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { RepositoriesService } from '../../services/repositories.service';
import { CommonModule } from '@angular/common';
import { NgxEchartsDirective, provideEcharts } from 'ngx-echarts';

@Component({
  selector: 'app-age',
  templateUrl: './age.component.html',
  styleUrl: './age.component.css',
  standalone: true,
  imports: [CommonModule, NgxEchartsDirective],
  providers: [provideEcharts()],
})
export class AgeComponent implements OnInit {
  repo: string = '';
  subscription: any;
  active_days = 0;

  years: any;
  max_values = {
    commits: 0,
    insertions: 0,
    deletions: 0,
  };
  charts: any[] = [];
  chart_type: keyof typeof this.max_values = 'commits';

  constructor(
    public repoService: RepositoriesService,
    public route: ActivatedRoute,
  ) {}

  ngOnInit() {
    this.route.params.subscribe((params) => this.getRepo(params));
  }

  getRepo({ name }: any) {
    this.repo = name;
    this.subscription = this.repoService
      .getRepoActivity(name)
      .subscribe((data) => this.setRepoActivity(data));
  }

  setRepoActivity(data: any) {
    const daily = data.by_time.daily;
    const commit_days = Object.keys(daily.commits);
    const { years, max_values, active_days } = prepareDailyActivity(
      commit_days,
      daily,
    );
    this.active_days = active_days;
    this.years = years;
    this.max_values = max_values;
    this.setHeatmap(this.chart_type);
  }

  setHeatmap(chart_type: keyof typeof this.max_values) {
    this.chart_type = chart_type;
    this.charts = commitCalender(
      this.years,
      this.max_values[chart_type],
      chart_type,
    );
  }
}

export const prepareDailyActivity = (commit_days: any, daily: any) => {
  const years: any = {};
  const max_values = {
    commits: 0,
    insertions: 0,
    deletions: 0,
  };
  let active_days = 0;

  commit_days.forEach((day: any) => {
    const [y] = day.split('-');
    active_days += 1;

    const commits = daily.commits[day];
    const insertions = daily.insertions[day];
    const deletions = daily.deletions[day];

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
      deletions,
    };

    if (years[y]) {
      years[y].push(row);
    } else {
      years[y] = [row];
    }
  });

  return { years, max_values, active_days };
};

export const commitCalender = (
  years: any,
  max_value: number,
  chart_type: any,
) => {
  return Object.keys(years)
    .sort((a, b) => {
      return +b - +a;
    })
    .map((year) => ({
      tooltip: {
        position: 'top',
        confine: true,
        formatter: (value: any) => {
          const data = years[year][value.dataIndex];
          return tooltip(data);
        },
      },

      visualMap: {
        min: 0,
        max: max_value,
        inRange: {
          color: ['#eee', '#7bc96f', '#196127'],
        },
      },

      calendar: [
        {
          range: year,
          cellSize: ['auto', 20],
        },
      ],

      series: [
        {
          type: 'heatmap',
          coordinateSystem: 'calendar',
          calendarIndex: 0,
          data: years[year].map((x: any) => [x.day, x[chart_type]]),
        },
      ],
    }));
};

const tooltip = (data: any) => {
  return `
        <div class="card bg-dark text-white">
            <div class="card-header bg-danger text-white py-1">
                ${data.day}
            </div>

            <table class="table-sm">
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
        </div>
    `;
};
