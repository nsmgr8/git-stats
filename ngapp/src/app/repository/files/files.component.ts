import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { CommonModule, formatDate } from '@angular/common';

import { RepositoriesService } from '../../services/repositories.service';
import { NgxEchartsModule, provideEcharts } from 'ngx-echarts';

@Component({
  selector: 'app-files',
  templateUrl: './files.component.html',
  standalone: true,
  imports: [CommonModule, RouterModule, NgxEchartsModule],
  providers: [provideEcharts()],
})
export class FilesComponent implements OnInit, OnDestroy {
  repo: string = '';
  subscriptions = new Set<any>();
  chartOptions: any;

  authors: any;
  summary: any;

  constructor(
    public repoService: RepositoriesService,
    public route: ActivatedRoute,
  ) {}

  ngOnInit() {
    this.route.params.subscribe((params) => this.getRepo(params));
  }

  ngOnDestroy() {
    this.subscriptions.forEach((x) => x.unsubscribe());
  }

  getRepo({ name }: any) {
    this.repo = name;
    this.subscriptions.add(
      this.repoService
        .getFilesHistory(name)
        .subscribe((data) => this.setFiles(data)),
    );
    this.subscriptions.add(
      this.repoService
        .getAuthors(name)
        .subscribe((data) => this.setAuthors(data)),
    );
    this.subscriptions.add(
      this.repoService
        .getRepoSummary(name)
        .subscribe((data) => this.setLines(data)),
    );
  }

  setLines(data: any) {
    const summary: any = {};
    data.forEach((x: any) => (summary[x.key] = x.value));
    this.summary = summary;
  }

  setAuthors(data: any) {
    const authors = Object.keys(data.lines);
    this.authors = authors
      .map((a) => {
        return {
          author: a,
          lines: data.lines[a],
          files: data.files[a],
        };
      })
      .sort((a, b) => b.lines - a.lines);
  }

  setFiles(data: any) {
    data = Object.values(data)
      .map((x: any) => {
        return {
          timestamp: x.timestamp * 1000,
          files: x.files,
        };
      })
      .sort((a, b) => {
        return a.timestamp - b.timestamp;
      });

    this.chartOptions = {
      title: {
        text: 'Number of files over time',
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          crossStyle: {
            color: '#999',
          },
        },
      },
      dataZoom: [
        {
          type: 'inside',
          start: 50,
          end: 100,
        },
        {
          start: 50,
          end: 100,
          handleIcon:
            'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
          handleSize: '80%',
          handleStyle: {
            color: '#fff',
            shadowBlur: 3,
            shadowColor: 'rgba(0, 0, 0, 0.6)',
            shadowOffsetX: 2,
            shadowOffsetY: 2,
          },
          labelFormatter: (_: any, value: any) =>
            formatDate(value, 'mediumDate', 'en-GB'),
        },
      ],
      xAxis: {
        type: 'category',
        data: data.map((x: any) => x.timestamp),
        axisLabel: {
          formatter: (value: any) => formatDate(value, 'mediumDate', 'en-GB'),
        },
        axisPointer: {
          label: {
            formatter: (value: any) =>
              formatDate(value.value, 'mediumDate', 'en-GB'),
          },
        },
      },
      yAxis: {},
      series: [
        {
          type: 'line',
          data: data.map((x: any) => x.files),
        },
      ],
    };
  }
}
