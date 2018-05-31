import { Component, OnInit } from '@angular/core';

import { RepositoriesService } from '../services/repositories.service';

@Component({
    selector: 'app-repositories',
    templateUrl: './repositories.component.html',
    styleUrls: ['./repositories.component.styl']
})
export class RepositoriesComponent implements OnInit {

    constructor(
        public repoService: RepositoriesService
    ) {
    }

    ngOnInit() {
    }

}
