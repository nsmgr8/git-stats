import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { RepositoriesService } from '../../services/repositories.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-tags',
  templateUrl: './tags.component.html',
  standalone: true,
  imports: [CommonModule],
})
export class TagsComponent implements OnInit {
  repo: string = '';
  tags: any;

  constructor(
    public repoService: RepositoriesService,
    public route: ActivatedRoute,
  ) {}

  ngOnInit() {
    this.route.params.subscribe((params) => this.getRepo(params));
  }

  getRepo({ name }: any) {
    this.repo = name;
    this.repoService.getTags(name).subscribe((data) => this.setTags(data));
  }

  setTags(data: any) {
    this.tags = data.map((x: any) => {
      const authors =
        (x.authors &&
          x.authors.sort((a: any, b: any) => b.commits - a.commits)) ||
        [];
      const commits = authors.reduce(
        (acc: number, val: any) => acc + val.commits,
        0,
      );
      return {
        tag: x.tag,
        timestamp: x.timestamp * 1000,
        authors,
        commits,
      };
    });
  }
}
