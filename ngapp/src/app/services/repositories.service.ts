import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class RepositoriesService {
  endpoint = '/workdir/data/';

  constructor(public http: HttpClient) {}

  get(path: string) {
    return this.http.get(`${this.endpoint}${path}`);
  }

  getRepositories() {
    return this.get('repos.json');
  }

  getRepoSummary(name: string) {
    return this.get(`${name}/summary.json`);
  }

  getRepoActivity(name: string) {
    return this.get(`${name}/activity.json`);
  }

  getLines(name: string) {
    return this.get(`${name}/lines.json`);
  }

  getFilesHistory(name: string) {
    return this.get(`${name}/files-history.json`);
  }

  getTags(name: string) {
    return this.get(`${name}/tags.json`);
  }

  getBranches(name: string) {
    return this.get(`${name}/branches.json`);
  }

  getAuthors(name: string) {
    return this.get(`${name}/authors.json`);
  }

  videoUrl(name: string) {
    return `${this.endpoint}${name}/history.mp4`;
  }

  hasVideo(name: string) {
    return this.http.head(this.videoUrl(name), {
      observe: 'response',
      responseType: 'blob',
    });
  }
}
