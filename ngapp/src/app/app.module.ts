import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';

import {NgbModule} from '@ng-bootstrap/ng-bootstrap';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { RepositoriesComponent } from './repositories/repositories.component';
import { RepositoryComponent } from './repository/repository/repository.component';
import { AuthorsComponent } from './repository/authors/authors.component';
import { AgeComponent } from './repository/age/age.component';
import { BranchesComponent } from './repository/branches/branches.component';
import { CommitsComponent } from './repository/commits/commits.component';
import { FilesComponent } from './repository/files/files.component';
import { LinesComponent } from './repository/lines/lines.component';
import { TagsComponent } from './repository/tags/tags.component';

@NgModule({
    declarations: [
        AppComponent,
        RepositoriesComponent,
        RepositoryComponent,
        AuthorsComponent,
        AgeComponent,
        BranchesComponent,
        CommitsComponent,
        FilesComponent,
        LinesComponent,
        TagsComponent
    ],
    imports: [
        BrowserModule,
        HttpClientModule,
        NgbModule.forRoot(),
        AppRoutingModule
    ],
    providers: [],
    bootstrap: [AppComponent]
})
export class AppModule { }
