import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { formatDate } from '@angular/common';

import { RepositoriesService } from '../../services/repositories.service';

@Component({
    selector: 'app-files',
    templateUrl: './files.component.html',
    styleUrls: ['./files.component.styl']
})
export class FilesComponent implements OnInit, OnDestroy {
    repo;
    subscription;
    chartOptions;

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

    ngOnDestroy() {
        if (this.subscription) {
            this.subscription.unsubscribe();
        }
    }

    getRepo({name}: any) {
        this.repo = name;
        this.subscription = this.repoService.getFilesHistory(name)
            .subscribe(
                data => this.setFiles(data)
            );
    }

    setFiles(data) {
        data = Object.values(data).map((x: any) => {
            return {
                timestamp: x.timestamp * 1000,
                files: x.files
            };
        }).sort((a, b) => {
            return a.timestamp - b.timestamp;
        });

        this.chartOptions = {
            title: {
                text: 'Number of files over time'
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    crossStyle: {
                        color: '#999'
                    }
                },
            },
            dataZoom: [{
                type: 'inside',
                start: 50,
                end: 100
            }, {
                start: 50,
                end: 100,
                handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
                handleSize: '80%',
                handleStyle: {
                    color: '#fff',
                    shadowBlur: 3,
                    shadowColor: 'rgba(0, 0, 0, 0.6)',
                    shadowOffsetX: 2,
                    shadowOffsetY: 2
                },
                labelFormatter: (_, value) => formatDate(value, 'mediumDate', 'en-GB')
            }],
            xAxis: {
                type: 'category',
                data: data.map(x => x.timestamp),
                axisLabel: {
                    formatter: (value) => formatDate(value, 'mediumDate', 'en-GB')
                },
                axisPointer: {
                    label: {
                        formatter: (value) => formatDate(value.value, 'mediumDate', 'en-GB')
                    }
                }
            },
            yAxis: {
            },
            series: [{
                type: 'line',
                data: data.map(x => x.files)
            }]
        };
    }
}
