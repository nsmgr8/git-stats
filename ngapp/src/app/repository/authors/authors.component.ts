import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';

import { RepositoriesService } from '../../services/repositories.service';
import { CommonModule } from '@angular/common';
import { PeriodPipe } from '../../pipes/period.pipe';
import { OrderToggleComponent } from '../../components/order-toggle/order-toggle.component';

@Component({
  selector: 'app-authors',
  templateUrl: './authors.component.html',
  styleUrl: './authors.component.css',
  standalone: true,
  imports: [CommonModule, RouterModule, PeriodPipe, OrderToggleComponent],
})
export class AuthorsComponent implements OnInit {
  subscription: any;
  authors: any;
  repo: string = '';
  order = {
    field: 'commits',
    direction: 1,
  };
  period_order: {
    field: 'commits' | 'insertions' | 'deletions';
    direction: number;
  } = {
    field: 'commits',
    direction: 1,
  };

  order_title = {
    commits: 'Commits',
    insertions: 'Lines Added',
    deletions: 'Lines Removed',
  };

  author_of_the_periods: { type: string; value: any }[] = [];

  constructor(
    public repoService: RepositoriesService,
    public route: ActivatedRoute,
  ) {}

  ngOnInit() {
    this.route.params.subscribe((params) => this.getRepo(params));
  }

  getRepo({ name }: any) {
    this.repo = name;
    this.subscription = this.repoService
      .getRepoActivity(name)
      .subscribe((data) => this.setRepoActivity(data));
  }

  setRepoActivity(data: any) {
    this.setAuthors(data);
    this.author_of_the_periods = ['weekly', 'monthly', 'yearly'].map(
      (period) => ({
        type: period,
        value: this.setAuthorOfThePeriod(data, period),
      }),
    );
  }

  setAuthors(data: any) {
    const authors = Object.keys(data.by_authors);
    this.authors = authors
      .map((a) => {
        let { commits, insertions, deletions } = data.by_authors[a].yearly;
        commits = (Object.values(commits) as number[]).reduce(
          (acc: number, val: number) => acc + val,
          0,
        );
        if (insertions) {
          insertions = (Object.values(insertions) as number[]).reduce(
            (acc: number, val: number) => acc + val,
            0,
          );
        }
        if (deletions) {
          deletions = (Object.values(deletions) as number[]).reduce(
            (acc: number, val: number) => acc + val,
            0,
          );
        }
        return {
          author: a,
          commits,
          insertions,
          deletions,
          ...data.authors_age[a],
        };
      })
      .sort((a, b) => {
        return b.commits - a.commits;
      });
  }

  toggleOrder(field: string) {
    if (this.order.field === field) {
      this.order.direction = -1 * this.order.direction;
    } else {
      this.order = { field, direction: 1 };
    }
    this.authors = this.authors.sort((a: any, b: any) => {
      return this.order.direction * (b[field] - a[field]);
    });
  }

  togglePeriodOrder(field: 'commits' | 'insertions' | 'deletions') {
    if (this.period_order.field === field) {
      this.period_order.direction = -1 * this.period_order.direction;
    } else {
      this.period_order = { field, direction: 1 };
    }

    this.author_of_the_periods = this.author_of_the_periods.map((x: any) => {
      return {
        ...x,
        value: x.value.map((y: any) => {
          return {
            ...y,
            data: y.data.sort((a: any, b: any) => {
              return this.period_order.direction * (b[field] - a[field]);
            }),
          };
        }),
      };
    });
  }

  setAuthorOfThePeriod(data: any, period: any) {
    const authors = Object.keys(data.by_authors);
    const rows: any = {};
    authors.forEach((a) => {
      const { commits, insertions, deletions } = data.by_authors[a][period];
      Object.keys(commits).forEach((key) => {
        const row = {
          author: a,
          commits: commits[key],
          insertions: insertions && insertions[key],
          deletions: deletions && deletions[key],
        };

        if (rows[key]) {
          rows[key].push(row);
        } else {
          rows[key] = [row];
        }
      });
    });

    return Object.keys(rows)
      .sort((a, b) => {
        return b.localeCompare(a);
      })
      .map((x) => {
        return {
          period: x,
          data: rows[x].sort((a: any, b: any) => b.commits - a.commits),
        };
      });
  }
}
