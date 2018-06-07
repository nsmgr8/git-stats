import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OrderToggleComponent } from './order-toggle/order-toggle.component';

@NgModule({
    imports: [
        CommonModule
    ],
    exports: [
        OrderToggleComponent
    ],
    declarations: [
        OrderToggleComponent
    ]
})
export class ComponentsModule { }
