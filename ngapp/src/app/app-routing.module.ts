import { NgModule } from '@angular/core';
import { Routes, RouterModule, ExtraOptions } from '@angular/router';

import { RepositoriesComponent } from './repositories/repositories.component';
import { RepositoryComponent } from './repository/repository/repository.component';
import { AgeComponent } from './repository/age/age.component';
import { AuthorsComponent } from './repository/authors/authors.component';
import { AuthorComponent } from './repository/author/author.component';
import { BranchesComponent } from './repository/branches/branches.component';
import { CommitsComponent } from './repository/commits/commits.component';
import { FilesComponent } from './repository/files/files.component';
import { LinesComponent } from './repository/lines/lines.component';
import { TagsComponent } from './repository/tags/tags.component';

const routes: Routes = [
    { path: '', component: RepositoriesComponent },
    { path: 'repo/:name', component: RepositoryComponent,
        children: [
            { path: '', redirectTo: 'authors', pathMatch: 'full' },
            { path: 'age', component: AgeComponent },
            { path: 'authors', component: AuthorsComponent },
            { path: 'author', component: AuthorComponent },
            { path: 'branches', component: BranchesComponent },
            { path: 'commits', component: CommitsComponent },
            { path: 'files', component: FilesComponent },
            { path: 'lines', component: LinesComponent },
            { path: 'tags', component: TagsComponent }
        ]
    }
];

export const routingConfiguration: ExtraOptions = {
    paramsInheritanceStrategy: 'always'
};


@NgModule({
    imports: [RouterModule.forRoot(routes, routingConfiguration)],
    exports: [RouterModule]
})
export class AppRoutingModule { }
