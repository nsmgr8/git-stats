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
    }
}
