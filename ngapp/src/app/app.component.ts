import { Component, OnInit } from '@angular/core';

import { RepositoriesService } from './services/repositories.service';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.styl']
})
export class AppComponent implements OnInit {
    last_updated;

    constructor(
        public repoService: RepositoriesService
    ) {
    }

    ngOnInit() {
        this.repoService.get('last_update.json')
            .subscribe((data: any) => this.last_updated = data.last_updated * 1000);
    }
}
