import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { RepositoriesService } from '../../services/repositories.service';

@Component({
    selector: 'app-lines',
    templateUrl: './lines.component.html',
    styleUrls: ['./lines.component.styl']
})
export class LinesComponent implements OnInit {
    repo;
    lines;
    lines_total;
    order = 'code';

    chart_options;

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
        this.repoService.getLines(name)
            .subscribe(
                data => this.setLines(data)
            );
    }

    setLines(data) {
        this.lines = Object.keys(data.lines)
            .filter(x => !['SUM', 'header'].includes(x))
            .map(x => {
                const d = data.lines[x];
                return {
                    lang: x,
                    ...d,
                    total: d.blank + d.comment + d.code
                };
            });

        this.lines_total = {
            ...data.lines.header,
            ...data.lines.SUM,
            total: data.lines.SUM.blank + data.lines.SUM.comment + data.lines.SUM.code
        };

        this.setChart();
    }

    toggleOrder(field) {
        this.order = field;
        this.lines = this.lines.sort((a, b) => b[field] - a[field]);
    }

    setChart() {
        this.chart_options = {
            series: [
                {
                    name: 'Lines of code',
                    type: 'pie',
                    label: {
                        normal: {
                            formatter: '{a|{a}}\n{hr|}\n  {b|{b}：}{c}  {per|{d}%}  ',
                            backgroundColor: '#eee',
                            borderColor: '#aaa',
                            borderWidth: 1,
                            borderRadius: 4,
                            rich: {
                                a: {
                                    color: '#999',
                                    lineHeight: 22,
                                    align: 'center'
                                },
                                hr: {
                                    borderColor: '#aaa',
                                    width: '100%',
                                    borderWidth: 0.5,
                                    height: 0
                                },
                                b: {
                                    fontSize: 16,
                                    lineHeight: 33
                                },
                                per: {
                                    color: '#eee',
                                    backgroundColor: '#334455',
                                    padding: [2, 4],
                                    borderRadius: 2
                                }
                            }
                        }
                    },
                    radius: [0, '55%'],
                    data: this.lines.slice(0, 5).map((x, i) => ({
                        value: x.code, name: x.lang, selected: i === 0
                    }))
                }
            ]
        };
    }
}
