import { Injectable } from '@angular/core';
import { Location } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Injectable({
    providedIn: 'root'
})
export class RepositoriesService {
    endpoint = '/data/';

    constructor(
        loc: Location,
        public http: HttpClient
    ) {
        this.endpoint = loc.prepareExternalUrl('/data/');
    }

    get(path) {
        return this.http.get(`${this.endpoint}${path}`);
    }

    getRepositories() {
        return this.get('repos.json');
    }

    getRepoSummary(name) {
        return this.get(`${name}/summary.json`);
    }

    getRepoActivity(name) {
        return this.get(`${name}/activity.json`);
    }

    getLines(name) {
        return this.get(`${name}/lines.json`);
    }

    getFilesHistory(name) {
        return this.get(`${name}/files-history.json`);
    }

    getTags(name) {
        return this.get(`${name}/tags.json`);
    }

    getBranches(name) {
        return this.get(`${name}/branches.json`);
    }

    getAuthors(name) {
        return this.get(`${name}/authors.json`);
    }

    videoUrl(name) {
        return `${this.endpoint}${name}/history.mp4`;
    }

    hasVideo(name) {
        return this.http.head(
            this.videoUrl(name),
            {observe: 'response', responseType: 'blob'}
        );
    }
}
