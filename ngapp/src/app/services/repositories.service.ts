import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
    providedIn: 'root'
})
export class RepositoriesService {
    endpoint = '/data/';

    constructor(
        public http: HttpClient
    ) {
    }

    get(path) {
        return this.http.get(`${this.endpoint}${path}`);
    }

    getRepositories() {
        return this.get('repos.json');
    }
}
